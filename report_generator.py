"""
PDF Report Generator for Business Intelligence Audits
Converts audit data into professional downloadable PDF
"""

from weasyprint import HTML
from datetime import datetime
import tempfile

def generate_pdf_report(audit_data):
    """
    Generates professional PDF from audit data
    Returns path to generated PDF file
    """
    
    # Extract data
    company_name = audit_data['company_name']
    audit_id = audit_data['id']
    waste_score = audit_data['intelligence_score']
    
    # Get waste zones from results
    results = audit_data.get('results', [])
    if results and results[0]:
        waste_zones = [r for r in results if r]
    else:
        waste_zones = []
    
    # Calculate totals
    total_hours = sum(z.get('time_wasted_monthly', 0) for z in waste_zones)
    estimated_cost = total_hours * 50  # KSh 50/hour average
    
    # Determine urgency
    if waste_score >= 80:
        urgency = "CRITICAL"
        urgency_color = "#dc2626"
    elif waste_score >= 60:
        urgency = "HIGH"
        urgency_color = "#ea580c"
    elif waste_score >= 40:
        urgency = "MEDIUM"
        urgency_color = "#f59e0b"
    else:
        urgency = "LOW"
        urgency_color = "#84cc16"
    
    # Build HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4;
                margin: 2cm;
            }}
            
            body {{
                font-family: 'Arial', sans-serif;
                color: #1f2937;
                line-height: 1.6;
            }}
            
            .header {{
                text-align: center;
                border-bottom: 3px solid #3b82f6;
                padding-bottom: 20px;
                margin-bottom: 30px;
            }}
            
            .header h1 {{
                color: #1e40af;
                font-size: 28px;
                margin: 0;
            }}
            
            .company {{
                font-size: 18px;
                color: #6b7280;
                margin-top: 10px;
            }}
            
            .score-box {{
                background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
                color: white;
                padding: 30px;
                border-radius: 10px;
                text-align: center;
                margin: 30px 0;
            }}
            
            .score {{
                font-size: 72px;
                font-weight: bold;
            }}
            
            .urgency-badge {{
                display: inline-block;
                background: {urgency_color};
                color: white;
                padding: 8px 20px;
                border-radius: 20px;
                font-weight: bold;
                margin-top: 10px;
            }}
            
            .summary {{
                background: #f3f4f6;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
            }}
            
            .summary h2 {{
                color: #1e40af;
                margin-top: 0;
            }}
            
            .stat {{
                background: white;
                padding: 15px;
                border-radius: 5px;
                margin: 10px 0;
                display: inline-block;
                width: 45%;
                margin-right: 2%;
            }}
            
            .stat-value {{
                font-size: 24px;
                font-weight: bold;
                color: #3b82f6;
            }}
            
            .stat-label {{
                font-size: 14px;
                color: #6b7280;
            }}
            
            .zone {{
                background: white;
                border: 1px solid #e5e7eb;
                border-left: 4px solid #3b82f6;
                padding: 20px;
                margin: 15px 0;
                border-radius: 5px;
                page-break-inside: avoid;
            }}
            
            .zone-header {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 15px;
            }}
            
            .zone-name {{
                font-size: 18px;
                font-weight: bold;
                color: #1f2937;
            }}
            
            .zone-score {{
                font-size: 24px;
                font-weight: bold;
                color: #3b82f6;
            }}
            
            .zone-detail {{
                display: inline-block;
                margin: 10px 20px 10px 0;
            }}
            
            .detail-label {{
                font-size: 12px;
                color: #6b7280;
                text-transform: uppercase;
            }}
            
            .detail-value {{
                font-size: 18px;
                font-weight: bold;
                color: #1f2937;
            }}
            
            .recommendation {{
                background: #eff6ff;
                padding: 15px;
                border-radius: 5px;
                border-left: 3px solid #3b82f6;
                margin-top: 10px;
            }}
            
            .rec-label {{
                font-size: 12px;
                color: #3b82f6;
                font-weight: bold;
                text-transform: uppercase;
            }}
            
            .complexity-badge {{
                display: inline-block;
                padding: 3px 10px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: bold;
                text-transform: uppercase;
            }}
            
            .complexity-low {{
                background: #d1fae5;
                color: #065f46;
            }}
            
            .complexity-medium {{
                background: #fed7aa;
                color: #92400e;
            }}
            
            .next-steps {{
                background: #f0fdf4;
                border: 2px solid #22c55e;
                padding: 20px;
                border-radius: 8px;
                margin: 30px 0;
            }}
            
            .next-steps h2 {{
                color: #15803d;
                margin-top: 0;
            }}
            
            .footer {{
                margin-top: 50px;
                padding-top: 20px;
                border-top: 2px solid #e5e7eb;
                text-align: center;
                color: #6b7280;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>BUSINESS INTELLIGENCE AUDIT REPORT</h1>
            <div class="company">{company_name}</div>
            <div style="font-size: 12px; color: #9ca3af; margin-top: 5px;">
                Generated: {datetime.now().strftime('%B %d, %Y')} | Report ID: #{audit_id}
            </div>
        </div>
        
        <div class="score-box">
            <div style="font-size: 16px; opacity: 0.9;">Intelligence Waste Score</div>
            <div class="score">{waste_score}/100</div>
            <div class="urgency-badge">{urgency} PRIORITY</div>
        </div>
        
        <div class="summary">
            <h2>Executive Summary</h2>
            <p>Our analysis identified significant opportunities to optimize your organization's use of human intelligence. Your team is spending valuable cognitive capacity on mechanical tasks that could be automated.</p>
            
            <div class="stat">
                <div class="stat-value">{total_hours}h</div>
                <div class="stat-label">Hours Wasted Monthly</div>
            </div>
            <div class="stat">
                <div class="stat-value">KSh {estimated_cost:,}</div>
                <div class="stat-label">Estimated Monthly Cost</div>
            </div>
        </div>
        
        <h2 style="color: #1e40af; border-bottom: 2px solid #3b82f6; padding-bottom: 10px;">Intelligence Waste Zones (Ranked by ROI)</h2>
    """
    
    # Add waste zones
    for i, zone in enumerate(waste_zones, 1):
        complexity = zone.get('automation_complexity', 'Medium')
        complexity_class = f"complexity-{complexity.lower()}"
        
        html_content += f"""
        <div class="zone">
            <div class="zone-header">
                <div>
                    <div class="zone-name">#{i}. {zone.get('waste_zone', 'Unknown')}</div>
                    <span class="complexity-badge {complexity_class}">{complexity} Complexity</span>
                </div>
                <div class="zone-score">{zone.get('waste_score', 0)}/100</div>
            </div>
            
            <div class="zone-detail">
                <div class="detail-label">Time Wasted/Month</div>
                <div class="detail-value">{zone.get('time_wasted_monthly', 0)}h</div>
            </div>
            <div class="zone-detail">
                <div class="detail-label">Estimated ROI</div>
                <div class="detail-value">{zone.get('estimated_roi', 0)}%</div>
            </div>
            <div class="zone-detail">
                <div class="detail-label">Monthly Cost</div>
                <div class="detail-value">KSh {zone.get('time_wasted_monthly', 0) * 50:,}</div>
            </div>
            
            <div class="recommendation">
                <div class="rec-label">Recommended Solution</div>
                <div>{zone.get('recommendation', 'Custom solution recommended')}</div>
            </div>
        </div>
        """
    
    html_content += f"""
        <div class="next-steps">
            <h2>🚀 Next Steps</h2>
            <p><strong>We recommend taking action in this order:</strong></p>
            <ol>
                <li><strong>Quick Wins (0-30 days):</strong> Address Low complexity zones for immediate ROI</li>
                <li><strong>Strategic Builds (30-90 days):</strong> Tackle Medium complexity opportunities</li>
                <li><strong>Free Consultation:</strong> Book 30-minute call to discuss roadmap</li>
            </ol>
            <p style="margin-top: 20px; text-align: center;">
                <strong>Ready to amplify your team's intelligence?</strong><br>
                Visit <strong style="color: #3b82f6;">eliombogo.com</strong> or email <strong style="color: #3b82f6;">eli@eliombogo.com</strong>
            </p>
        </div>
        
        <div class="footer">
            <p><strong>About This Audit:</strong> Analysis conducted using proprietary diagnostic framework evaluating where human cognitive capacity is spent on mechanical tasks.</p>
            <p style="margin-top: 10px;">© {datetime.now().year} Eli Ombogo - AI Systems Architect & Intelligence Auditor</p>
        </div>
    </body>
    </html>
    """
    
    # Generate PDF
    pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    HTML(string=html_content).write_pdf(pdf_file.name)
    
    return pdf_file.name
