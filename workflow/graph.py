from langgraph.graph import StateGraph, END
from workflow.state import AgentState
from workflow.nodes import research_node, analyze_node, draft_node

def create_graph():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("research", research_node)
    workflow.add_node("analyze", analyze_node)
    workflow.add_node("draft", draft_node)
    
    # Set entry point
    workflow.set_entry_point("research")
    
    # Add edges
    workflow.add_edge("research", "analyze")
    workflow.add_edge("analyze", "draft")
    workflow.add_edge("draft", END)
    
    return workflow.compile()
