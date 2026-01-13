from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        port=os.getenv('DB_PORT'),
        cursor_factory=RealDictCursor
    )

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'Business Intelligence Auditor'})

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        
        required = ['company_name', 'industry', 'team_size', 'responses']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing: {field}'}), 400
        
        session_id = f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        from analyzer import analyze_intelligence_waste
        analysis = analyze_intelligence_waste(data['responses'])
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO audits (
                session_id, company_name, industry, team_size, 
                responses, intelligence_score, opportunities, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            RETURNING id
        """, (
            session_id,
            data['company_name'],
            data['industry'],
            data['team_size'],
            json.dumps(data['responses']),
            analysis['waste_score'],
            json.dumps(analysis['opportunities'])
        ))
        
        audit_id = cur.fetchone()['id']
        
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
        
        conn.commit()
        
        from cip_engine import CIPEngine
        cip = CIPEngine()
        cip.log_patterns({
            'industry': data['industry'],
            'waste_score': analysis['waste_score'],
            'top_waste_zone': analysis['waste_zones'][0]['name'] if analysis['waste_zones'] else None
        })
        cip.close()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'session_id': session_id,
            'audit_id': audit_id,
            'waste_score': analysis['waste_score'],
            'total_hours_wasted': analysis['total_hours_wasted'],
            'waste_zones': analysis['waste_zones'][:3],
            'report_url': f'/api/report/{audit_id}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/report/<int:audit_id>', methods=['GET'])
def get_report(audit_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT a.*, 
                   json_agg(json_build_object(
                       'waste_zone', ar.waste_zone,
                       'waste_score', ar.waste_score,
                       'time_wasted_monthly', ar.time_wasted_monthly,
                       'automation_complexity', ar.automation_complexity,
                       'estimated_roi', ar.estimated_roi,
                       'recommendation', ar.recommendation
                   )) as results
            FROM audits a
            LEFT JOIN audit_results ar ON ar.audit_id = a.id
            WHERE a.id = %s
            GROUP BY a.id
        """, (audit_id,))
        
        audit = cur.fetchone()
        cur.close()
        conn.close()
        
        if not audit:
            return jsonify({'error': 'Audit not found'}), 404
        
        from report_generator import generate_pdf_report
        pdf_path = generate_pdf_report(audit)
        
        return send_file(
            pdf_path, 
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'intelligence_audit_{audit_id}.pdf'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cip/insights', methods=['GET'])
def get_cip_insights():
    try:
        from cip_engine import CIPEngine
        cip = CIPEngine()
        report = cip.generate_monthly_report()
        cip.close()
        
        return jsonify(report)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port)