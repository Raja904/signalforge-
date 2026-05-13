from typing import TypedDict, List, Annotated, Optional
import operator

class AgentState(TypedDict):
    # Inputs
    prospect_name: str
    company_name: str
    role: str
    product_description: str
    sender_name: str
    sender_role: str
    
    # Internal State
    signals: List[dict]
    selected_hook: Optional[str]
    hook_reasoning: Optional[str]
    
    # Outputs
    email_subject: Optional[str]
    email_body: Optional[str]
    linkedin_draft: Optional[str]
    quality_score: Optional[int]
    
    # Edge Case Flags
    is_ghost: bool
    is_stale: bool
    is_ambiguous: bool
    
    # Logs for UI
    logs: Annotated[List[str], operator.add]
