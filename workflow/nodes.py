import json
from services.serper import get_prospect_signals
from services.mistral_client import call_mistral
from workflow.state import AgentState

def research_node(state: AgentState):
    name = state['prospect_name']
    company = state['company_name']
    
    signals, queries = get_prospect_signals(name, company)
    
    # Create detailed logs for each query
    search_logs = [f"🔍 Searching: \"{q}\"" for q in queries]
    
    is_ghost = len(signals) == 0
    
    return {
        "signals": signals,
        "is_ghost": is_ghost,
        "logs": search_logs + [f"📄 Found {len(signals)} potential signals — scoring relevance..."]
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
    
    # Format signals for the LLM
    signals_text = "\n".join([f"- {s['title']}: {s['snippet']} (Source: {s['link']})" for s in signals[:10]])
    
    prompt = f"""
    Analyze the following research signals for {name}, who works as {role} at {company}.
    We are selling: {product}
    
    Signals:
    {signals_text}
    
    Task:
    1. Identify the single most relevant "hook" for a cold outreach email.
    2. Detect if the data is stale (e.g. no news in last 2 years).
    3. Detect if the company name is ambiguous (signals refer to multiple different companies).
    
    Return your analysis as a JSON object with the following keys:
    "selected_hook": "the hook text",
    "reasoning": "why this is the best hook",
    "is_stale": true/false,
    "is_ambiguous": true/false
    """
    
    res_text = call_mistral(prompt, is_json=True)
    try:
        res = json.loads(res_text)
    except:
        res = {"selected_hook": "Recent company activity", "reasoning": "Error parsing LLM response", "is_stale": False, "is_ambiguous": False}
        
    return {
        "selected_hook": res.get("selected_hook"),
        "hook_reasoning": res.get("reasoning"),
        "is_stale": res.get("is_stale", False),
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
    
    prompt = f"""
    Write a cold outreach email and a LinkedIn message to {name} at {company}.
    Role: {role}
    Product being sold: {product}
    The Hook to use: {hook}
    
    Sender Info:
    Name: {sender_name}
    Role: {sender_role}
    
    The email should be:
    - Short (under 150 words)
    - Specific (not generic)
    - Have a clear call to action
    - END with 'Best,' followed by {sender_name} and {sender_role}. 
    - DO NOT use any placeholders like [Your Name], [Contact Info], etc.
    
    Return as a JSON object:
    "email_subject": "...",
    "email_body": "...",
    "linkedin_draft": "...",
    "quality_score": 1-10 (how personalized it is)
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
