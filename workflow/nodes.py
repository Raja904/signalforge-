import json
from services.serper import get_prospect_signals
from services.mistral_client import call_mistral
from workflow.state import AgentState

def research_node(state: AgentState):
    name = state['prospect_name']
    company = state['company_name']
    role = state['role']
    
    signals, queries = get_prospect_signals(name, company, role)
    
    # Strict Filter: signal must mention BOTH name AND company
    relevant_signals = [
        s for s in signals 
        if name.lower() in (s.get('snippet', '') + s.get('title', '')).lower()
        and company.lower() in (s.get('snippet', '') + s.get('title', '')).lower()
    ]
    
    is_ghost = len(relevant_signals) == 0
    
    return {
        "signals": relevant_signals,
        "is_ghost": is_ghost,
        "logs": [f"🔍 Searching: \"{q}\"" for q in queries] + 
                [f"📄 Found {len(relevant_signals)} relevant signals (filtered from {len(signals)} total)..."]
    }

def analyze_node(state: AgentState):
    signals = state['signals']
    name = state['prospect_name']
    company = state['company_name']
    role = state['role']
    product = state['product_description']
    
    if state['is_ghost']:
        return {
            "selected_hook": f"Standard industry hook for {role}",
            "hook_reasoning": "No specific signals found. Falling back to role-based template.",
            "logs": ["No signals found. Using fallback hook."]
        }
    
    # Format signals for the LLM with DATES
    signals_text = "\n".join([f"- {s['title']} (Date: {s.get('date', 'Unknown')}): {s['snippet']} (Source: {s['link']})" for s in signals[:10]])
    
    # Unique LinkedIn profiles pre-check
    unique_links = set(s.get('link', '') for s in signals if 'linkedin.com/in/' in s.get('link', ''))
    ambiguity_hint = ""
    if len(unique_links) > 2:
        ambiguity_hint = f"\nCRITICAL WARNING: Found {len(unique_links)} different LinkedIn profiles for this name+company combination. This strongly suggests an AMBIGUOUS prospect.\n"
    
    prompt = f"""
    Analyze the following research signals for {name}, who works as {role} at {company}.
    We are selling: {product}
    
    {ambiguity_hint}
    
    Signals:
    {signals_text}
    
    IMPORTANT RULES:
    - If {ambiguity_hint != ""} or multiple different LinkedIn profile URLs exist for the same name+company, you MUST set is_ambiguous=true.
    - If signals show they LEFT {company} or joined another company, set is_stale=true.
    - If most relevant signals are older than 2 years AND there is no recent 2024/2025 activity, set is_stale=true.
    - Company news alone does NOT mean the prospect's data is fresh.
    
    Return your analysis as a JSON object:
    "selected_hook": "...",
    "reasoning": "...",
    "is_stale": true/false,
    "stale_reason": "...",
    "is_ghost": true/false,
    "is_ambiguous": true/false
    """
    
    res_text = call_mistral(prompt, is_json=True)
    try:
        res = json.loads(res_text)
    except:
        res = {"selected_hook": "Recent activity", "reasoning": "Error parsing", "is_stale": False, "is_ghost": False, "is_ambiguous": False}
        
    return {
        "selected_hook": res.get("selected_hook"),
        "hook_reasoning": res.get("reasoning"),
        "is_stale": res.get("is_stale", False),
        "stale_reason": res.get("stale_reason"),
        "is_ghost": state['is_ghost'] or res.get("is_ghost", False),
        "is_ambiguous": res.get("is_ambiguous", False),
        "logs": [f"🎯 Hook selected: \"{res.get('selected_hook')[:50]}...\" (confidence: high)"]
    }

def draft_node(state: AgentState):
    name = state['prospect_name']
    company = state['company_name']
    role = state['role']
    product = state['product_description']
    hook = state['selected_hook']
    sender_name = state.get('sender_name', 'Your Name')
    sender_role = state.get('sender_role', 'Sales Representative')
    sender_company = state.get('sender_company', 'Our Company')
    
    prompt = f"""
    Write a cold outreach email and a LinkedIn message to {name} at {company}.
    Role: {role}
    Product being sold: {product}
    The Hook to use: {hook}
    Research Context: {"GHOST (No specific research found)" if state.get('is_ghost') else "RESEARCHED (Specific signals found)"}
    Staleness: {"STALE (Data might be old)" if state.get('is_stale') else "FRESH"}
    
    Sender Info:
    Name: {sender_name}
    Role: {sender_role}
    Company: {sender_company}
    
    The email and LinkedIn message should be:
    - Short (under 150 words)
    - Specific (not generic)
    - Have a clear call to action
    - END with 'Best,' followed by {sender_name}, {sender_role} at {sender_company}. 
    - DO NOT use any placeholders.
    
    Return as a JSON object with:
    "email_subject": "...",
    "email_body": "...",
    "linkedin_draft": "...",
    "quality_score": 1-10 
    
    QUALITY SCORE RUBRIC (Strictly follow this):
    - 1-3: Generic pitch. Hook is weak or generic (e.g. "saw you are working at [company]").
    - 4-6: Mentions role/company correctly but lacks a deep personal/recent signal. 
    - 7-8: Uses a specific research signal (news, post, achievement) effectively.
    - 9-10: Perfect personalization that makes it look like you spent 30 mins researching.
    
    IMPORTANT: If Research Context is GHOST or Staleness is STALE, the MAX score allowed is 5.
    """
    
    res_text = call_mistral(prompt, is_json=True)
    try:
        res = json.loads(res_text)
    except:
        res = {"email_subject": "Hello from Zamp", "email_body": f"Hi {name}, I saw you are at {company}...", "linkedin_draft": "Hi, let's connect!", "quality_score": 5}
        
    return {
        "email_subject": res.get("email_subject"),
        "email_body": res.get("email_body"),
        "linkedin_draft": res.get("linkedin_draft"),
        "quality_score": res.get("quality_score"),
        "logs": [
            "✍️ Generating email draft...",
            "✍️ Generating LinkedIn message...",
            f"✅ Done — quality score: {res.get('quality_score', 0)}/10"
        ]
    }
