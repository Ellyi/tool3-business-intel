"""
CIP Engine - Contextual Intelligence Protocol
Makes Tool #3 LEARN from usage and generate market intelligence
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
import json
from datetime import datetime

class CIPEngine:
    """
    Learning system that:
    1. Logs patterns from each audit
    2. Analyzes trends across all audits
    3. Generates market intelligence reports
    4. Identifies product opportunities
    """
    
    def __init__(self):
        self.conn = self._get_connection()
    
    def _get_connection(self):
        return psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=os.getenv('DB_PORT'),
            cursor_factory=RealDictCursor
        )
    
    def log_patterns(self, audit_data):
        """
        Called after each audit to log patterns
        Runs automatically every time someone completes audit
        """
        cur = self.conn.cursor()
        
        # Log industry waste patterns
        industry = audit_data.get('industry')
        waste_score = audit_data.get('waste_score')
        
        if industry and waste_score:
            cur.execute("""
                INSERT INTO audit_patterns (pattern_type, pattern_data, frequency, avg_score, last_updated)
                VALUES ('industry_waste', %s, 1, %s, NOW())
                ON CONFLICT (pattern_type, pattern_data)
                DO UPDATE SET 
                    frequency = audit_patterns.frequency + 1,
                    avg_score = (audit_patterns.avg_score * audit_patterns.frequency + EXCLUDED.avg_score) / (audit_patterns.frequency + 1),
                    last_updated = NOW()
            """, (json.dumps({'industry': industry}), waste_score))
        
        # Log waste zone frequency
        top_zone = audit_data.get('top_waste_zone')
        if top_zone:
            cur.execute("""
                INSERT INTO audit_patterns (pattern_type, pattern_data, frequency, last_updated)
                VALUES ('waste_zone_frequency', %s, 1, NOW())
                ON CONFLICT (pattern_type, pattern_data)
                DO UPDATE SET 
                    frequency = audit_patterns.frequency + 1,
                    last_updated = NOW()
            """, (json.dumps({'zone': top_zone}),))
        
        self.conn.commit()
        cur.close()
        
        # Check if we should run analysis (every 10 audits)
        self._check_analysis_trigger()
    
    def _check_analysis_trigger(self):
        """
        Runs pattern analysis every 10 audits
        """
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) as count FROM audits")
        count = cur.fetchone()['count']
        cur.close()
        
        if count % 10 == 0:
            self.analyze_patterns()
    
    def analyze_patterns(self):
        """
        Analyzes accumulated audit data
        Generates insights about market trends
        """
        cur = self.conn.cursor()
        
        # Find most common waste zones
        cur.execute("""
            SELECT ar.waste_zone, 
                   COUNT(*) as frequency, 
                   AVG(ar.waste_score) as avg_score
            FROM audit_results ar
            GROUP BY ar.waste_zone
            ORDER BY frequency DESC
            LIMIT 5
        """)
        top_zones = cur.fetchall()
        
        # Find industry with highest waste
        cur.execute("""
            SELECT industry, 
                   AVG(intelligence_score) as avg_waste, 
                   COUNT(*) as count
            FROM audits
            WHERE industry IS NOT NULL
            GROUP BY industry
            HAVING COUNT(*) >= 3
            ORDER BY avg_waste DESC
        """)
        industry_trends = cur.fetchall()
        
        # Generate insights
        if top_zones:
            most_common = top_zones[0]
            insight = f"Most common waste zone: {most_common['waste_zone']} ({most_common['frequency']} occurrences, avg score {most_common['avg_score']:.1f})"
            
            # Save insight
            cur.execute("""
                INSERT INTO intelligence_insights (
                    insight_type, insight_text, confidence, supporting_data, generated_at
                ) VALUES (%s, %s, %s, %s, NOW())
            """, (
                'waste_zone_leader',
                insight,
                0.95,
                json.dumps({
                    'zone': most_common['waste_zone'],
                    'frequency': int(most_common['frequency']),
                    'avg_score': float(most_common['avg_score'])
                })
            ))
        
        if industry_trends:
            highest_waste = industry_trends[0]
            insight = f"Industry with highest intelligence waste: {highest_waste['industry']} (avg {highest_waste['avg_waste']:.1f} from {highest_waste['count']} audits)"
            
            cur.execute("""
                INSERT INTO intelligence_insights (
                    insight_type, insight_text, confidence, supporting_data, generated_at
                ) VALUES (%s, %s, %s, %s, NOW())
            """, (
                'industry_leader',
                insight,
                0.90,
                json.dumps({
                    'industry': highest_waste['industry'],
                    'avg_waste': float(highest_waste['avg_waste']),
                    'sample_size': int(highest_waste['count'])
                })
            ))
        
        self.conn.commit()
        cur.close()
    
    def generate_monthly_report(self):
        """
        Generates comprehensive intelligence report for Eli
        Shows what we learned from all audits
        """
        cur = self.conn.cursor()
        
        # Total audits
        cur.execute("SELECT COUNT(*) as total FROM audits")
        total_audits = cur.fetchone()['total']
        
        # Average waste score
        cur.execute("SELECT AVG(intelligence_score) as avg_score FROM audits")
        avg_score_result = cur.fetchone()
        avg_score = float(avg_score_result['avg_score']) if avg_score_result['avg_score'] else 0
        
        # Top waste zones
        cur.execute("""
            SELECT waste_zone, 
                   COUNT(*) as frequency, 
                   AVG(waste_score) as avg_score
            FROM audit_results
            GROUP BY waste_zone
            ORDER BY frequency DESC
            LIMIT 10
        """)
        top_zones = cur.fetchall()
        
        # Market opportunities (zones with high frequency = templates to build)
        opportunities = []
        for zone in top_zones[:3]:
            if zone['frequency'] >= 5:
                opportunities.append({
                    'opportunity': f"Build {zone['waste_zone']} AI template",
                    'market_size': int(zone['frequency']),
                    'avg_pain': float(zone['avg_score']),
                    'potential_revenue': int(zone['frequency']) * 5000  # KSh 5K per client estimate
                })
        
        # Recent insights
        cur.execute("""
            SELECT insight_type, insight_text, confidence, supporting_data
            FROM intelligence_insights
            WHERE generated_at >= NOW() - INTERVAL '30 days'
            ORDER BY confidence DESC, generated_at DESC
            LIMIT 5
        """)
        recent_insights = cur.fetchall()
        
        cur.close()
        
        return {
            'period': 'Last 30 days',
            'total_audits': int(total_audits),
            'avg_waste_score': avg_score,
            'top_waste_zones': [
                {
                    'zone': z['waste_zone'],
                    'frequency': int(z['frequency']),
                    'avg_score': float(z['avg_score'])
                }
                for z in top_zones
            ],
            'market_opportunities': opportunities,
            'insights': [
                {
                    'type': i['insight_type'],
                    'text': i['insight_text'],
                    'confidence': float(i['confidence'])
                }
                for i in recent_insights
            ],
            'recommendations': self._generate_recommendations(opportunities)
        }
    
    def _generate_recommendations(self, opportunities):
        """
        Generates actionable recommendations based on patterns
        """
        recommendations = []
        
        if opportunities:
            top_opp = opportunities[0]
            recommendations.append(
                f"BUILD: {top_opp['opportunity']} - {top_opp['market_size']} companies need this (KSh {top_opp['potential_revenue']:,} potential)"
            )
        
        return recommendations
    
    def close(self):
        if self.conn:
            self.conn.close()
