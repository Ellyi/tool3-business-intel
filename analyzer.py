"""
Business Intelligence Waste Analyzer
Detects where businesses waste human intelligence on mechanical tasks
"""

def analyze_intelligence_waste(responses):
    """
    Analyzes 8 questionnaire responses
    Returns waste_score (0-100) and specific waste zones
    """
    
    waste_zones = []
    total_score = 0
    
    # Question 1: Repetitive explanations → Knowledge Bottleneck
    if responses.get('q1'):
        score = calculate_score(responses['q1'], ['every', 'always', 'repeatedly', 'constantly', 'daily'])
        if score > 30:
            waste_zones.append({
                'name': 'Knowledge Bottleneck',
                'score': score,
                'time_wasted': int((score / 100) * 20),  # Up to 20 hrs/month
                'complexity': 'Low',
                'roi': 250,
                'recommendation': 'Build internal knowledge base with AI search. Eliminate repeat explanations.'
            })
        total_score += score
    
    # Question 2: Repetitive data analysis → Repetitive Analysis
    if responses.get('q2'):
        score = calculate_score(responses['q2'], ['same', 'metrics', 'reports', 'dashboard', 'spreadsheet'])
        if score > 30:
            waste_zones.append({
                'name': 'Repetitive Analysis',
                'score': score,
                'time_wasted': int((score / 100) * 30),
                'complexity': 'Medium',
                'roi': 180,
                'recommendation': 'Automate recurring analysis with AI dashboard. Decision-ready insights instantly.'
            })
        total_score += score
    
    # Question 3: Information access delays → Information Access Gap
    if responses.get('q3'):
        score = calculate_score(responses['q3'], ['look up', 'search', 'find', 'minutes', 'time'])
        if score > 30:
            waste_zones.append({
                'name': 'Information Access Gap',
                'score': score,
                'time_wasted': int((score / 100) * 15),
                'complexity': 'Low',
                'roi': 300,
                'recommendation': 'Build AI customer support layer. Instant answers from company knowledge.'
            })
        total_score += score
    
    # Question 4: Manual data compilation → Data Integration Gap
    if responses.get('q4'):
        score = calculate_score(responses['q4'], ['manual', 'combine', 'multiple', 'sources', 'compile'])
        if score > 30:
            waste_zones.append({
                'name': 'Data Integration Gap',
                'score': score,
                'time_wasted': int((score / 100) * 40),
                'complexity': 'Medium',
                'roi': 200,
                'recommendation': 'Connect data sources with automated pipeline. Real-time unified reports.'
            })
        total_score += score
    
    # Question 5: Rule-based checks → Rule-Based Decisions
    if responses.get('q5'):
        score = calculate_score(responses['q5'], ['if', 'then', 'check', 'verify', 'approve'])
        if score > 30:
            waste_zones.append({
                'name': 'Rule-Based Decisions',
                'score': score,
                'time_wasted': int((score / 100) * 25),
                'complexity': 'Low',
                'roi': 220,
                'recommendation': 'Automate if/then logic with AI monitoring. Human only for exceptions.'
            })
        total_score += score
    
    # Question 6: Obvious inefficiencies → Acknowledged Pain Points
    if responses.get('q6'):
        score = calculate_score(responses['q6'], ['better way', 'frustrated', 'waste', 'inefficient'])
        if score > 30:
            waste_zones.append({
                'name': 'Acknowledged Pain Points',
                'score': score,
                'time_wasted': int((score / 100) * 35),
                'complexity': 'Varies',
                'roi': 150,
                'recommendation': 'High-priority fix. Team already knows this needs solving.'
            })
        total_score += score
    
    # Question 7: Mechanical tasks → Mechanical Tasks
    if responses.get('q7'):
        score = calculate_score(responses['q7'], ['repetitive', 'copy', 'paste', 'same thing', 'no thinking'])
        if score > 30:
            waste_zones.append({
                'name': 'Mechanical Tasks',
                'score': score,
                'time_wasted': int((score / 100) * 45),
                'complexity': 'Low',
                'roi': 280,
                'recommendation': 'Pure automation opportunity. No creativity required, high ROI.'
            })
        total_score += score
    
    # Question 8: Knowledge silos → Knowledge Silos
    if responses.get('q8'):
        score = calculate_score(responses['q8'], ['only', 'person', 'knows', 'head', 'ask'])
        if score > 30:
            waste_zones.append({
                'name': 'Knowledge Silos',
                'score': score,
                'time_wasted': int((score / 100) * 20),
                'complexity': 'Medium',
                'roi': 190,
                'recommendation': 'Capture tribal knowledge in AI system. Team-wide access, not person-dependent.'
            })
        total_score += score
    
    # Calculate average waste score
    num_responses = len([r for r in responses.values() if r])
    waste_score = int(total_score / num_responses) if num_responses > 0 else 0
    
    # Sort by ROI (highest first)
    waste_zones.sort(key=lambda x: x['roi'], reverse=True)
    
    # Total hours wasted
    total_hours_wasted = sum(z['time_wasted'] for z in waste_zones)
    
    return {
        'waste_score': waste_score,
        'total_hours_wasted': total_hours_wasted,
        'waste_zones': waste_zones,
        'opportunities': {
            'top_zone': waste_zones[0]['name'] if waste_zones else None,
            'quick_wins': [z for z in waste_zones if z['complexity'] == 'Low']
        }
    }

def calculate_score(text, keywords):
    """
    Scores response based on keyword presence
    Base score + bonus for each keyword found
    """
    if not text:
        return 0
    
    text_lower = text.lower()
    score = 40  # Base score for having the issue
    
    for keyword in keywords:
        if keyword in text_lower:
            score += 10
    
    return min(score, 100)  # Cap at 100

