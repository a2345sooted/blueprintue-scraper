import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional

class AgentState(TypedDict):
    blueprint_code: str
    summary: str

def summarize_blueprint_node(state: AgentState):
    """
    Summarization node.
    """
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    llm = ChatOpenAI(model=model_name)
    
    system_prompt = (
        "You are an expert in Unreal Engine blueprints. "
        "Analyze the provided blueprint code and provide a comprehensive summary in Markdown format. "
        "The summary should include:\n"
        "1. **High-Level Summary**: A clear, concise overview of what the blueprint does.\n"
        "2. **Detailed Breakdown**: A thorough, step-by-step technical explanation of the nodes, "
        "logic flow, variables, and events involved. Be explicit about how the logic connects."
    )
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Please analyze and summarize this Unreal Engine blueprint code:\n\n{state['blueprint_code']}")
    ]
    
    response = llm.invoke(messages)
    return {"summary": response.content}

def create_summarizer_agent():
    """
    Creates a simple one-shot summarizer agent.
    """
    workflow = StateGraph(AgentState)
    
    workflow.add_node("summarizer", summarize_blueprint_node)
    workflow.set_entry_point("summarizer")
    workflow.add_edge("summarizer", END)
    
    return workflow.compile()
