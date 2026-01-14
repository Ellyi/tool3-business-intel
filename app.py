from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
import secrets
from analyzer import analyze_intelligence_waste
from cip_engine import CIPEngine
from report_generator import generate_pdf_report

app = Flask(__name__)
CORS(app)

# Database connection
def get_db():
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME', 'railway'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD'),
        port=os.getenv('DB_PORT', 5432)
    )

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'tool3-business-intel'})

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    
    # Extract data
    company_name = data.get('company_name')
    industry = data.get('industry')
    team_size = data.get('team_size')
    responses = data.get('responses')
    
    # Analyze intelligence waste
    analysis = analyze_intelligence_waste(responses)
    
    # Store in database
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Insert audit
    cur.execute("""
        INSERT INTO audits (company_name, industry, team_size, responses, intelligence_score, opportunities)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        company_name,
        industry,
        team_size,
        responses,
        analysis['waste_score'],
        analysis
    ))
    
    audit_id = cur.fetchone()['id']
    
    # Insert waste zones
    for zone in analysis['waste_zones']:
        cur.execute("""
            INSERT INTO audit_results (
                audit_id, waste_zone, waste_score, time_wasted_monthly,
                automation_complexity, estimated_roi, recommendation
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            audit_id,
            zone['name'],
            zone['score'],
            zone['time_wasted'],
            zone['complexity'],
            zone['roi'],
            zone['recommendation']
        ))
    
    # Generate session for Nuru handoff
    session_id = secrets.token_urlsafe(32)
    
    user_context = {
        'company_name': company_name,
        'industry': industry,
        'team_size': team_size,
        'waste_score': analysis['waste_score'],
        'total_hours_wasted': analysis['total_hours_wasted'],
        'top_waste_zones': analysis['waste_zones'][:3],
        'audit_completed_at': datetime.now().isoformat()
    }
    
    cur.execute("""
        INSERT INTO sessions (session_id, audit_id, user_context)
        VALUES (%s, %s, %s)
    """, (session_id, audit_id, user_context))
    
    conn.commit()
    
    # CIP: Log patterns
    cip = CIPEngine()
    cip.log_patterns({
        'industry': industry,
        'waste_score': analysis['waste_score'],
        'top_waste_zone': analysis['waste_zones'][0]['name'] if analysis['waste_zones'] else None
    })
    
    cur.close()
    conn.close()
    
    return jsonify({
        'audit_id': audit_id,
        'session_id': session_id,
        'waste_score': analysis['waste_score'],
        'total_hours_wasted': analysis['total_hours_wasted'],
        'waste_zones': analysis['waste_zones']
    })

@app.route('/api/session/<session_id>', methods=['GET'])
def get_session(session_id):
    """API endpoint for Nuru to fetch audit context"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("""
        SELECT user_context, audit_id, created_at
        FROM sessions
        WHERE session_id = %s AND expires_at > NOW()
    """, (session_id,))
    
    session = cur.fetchone()
    
    if not session:
        cur.close()
        conn.close()
        return jsonify({'error': 'Session not found or expired'}), 404
    
    # Update access tracking
    cur.execute("""
        UPDATE sessions
        SET accessed_count = accessed_count + 1,
            last_accessed = NOW()
        WHERE session_id = %s
    """, (session_id,))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify(session['user_context'])

@app.route('/api/report/<int:audit_id>', methods=['GET'])
def download_report(audit_id):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("SELECT * FROM audits WHERE id = %s", (audit_id,))
    audit = cur.fetchone()
    
    cur.execute("SELECT * FROM audit_results WHERE audit_id = %s", (audit_id,))
    results = cur.fetchall()
    
    cur.close()
    conn.close()
    
    pdf_path = generate_pdf_report(audit, results)
    
    return send_file(pdf_path, as_attachment=True, download_name=f'intelligence_audit_{audit_id}.pdf')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))