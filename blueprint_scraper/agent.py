import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional

class AgentState(TypedDict):
    blueprint_code: str
    summary: str
    feedback: Optional[str]
    iteration_count: int

def summarize_blueprint_node(state: AgentState):
    """
    Initial summarization node.
    """
    llm = ChatOpenAI(model="gpt-5.2-2025-12-11")
    
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
    return {"summary": response.content, "iteration_count": 1}

def check_summary_node(state: AgentState):
    """
    Checks the summary for accuracy and completeness.
    """
    llm = ChatOpenAI(model="gpt-5.2-2025-12-11")
    
    check_prompt = (
        "You are a quality assurance expert for Unreal Engine blueprint documentation. "
        "Your task is to review a generated summary against the original blueprint code. "
        "Identify any inaccuracies, missing logic, or areas that are unclear for a UE developer. "
        "If the summary is excellent and accurate, respond with 'PASSED'. "
        "Otherwise, provide specific, constructive feedback on what needs to be fixed or added."
    )
    
    messages = [
        SystemMessage(content=check_prompt),
        HumanMessage(content=f"BLUEPRINT CODE:\n{state['blueprint_code']}\n\nGENERATED SUMMARY:\n{state['summary']}")
    ]
    
    response = llm.invoke(messages)
    feedback = response.content.strip()
    return {"feedback": feedback}

def repair_summary_node(state: AgentState):
    """
    Repairs the summary based on feedback.
    """
    llm = ChatOpenAI(model="gpt-5.2-2025-12-11")
    
    repair_prompt = (
        "You are an expert in Unreal Engine blueprints. "
        "You need to improve an existing blueprint summary based on specific feedback. "
        "Ensure the final summary remains in the required Markdown format with High-Level Summary and Detailed Breakdown."
    )
    
    messages = [
        SystemMessage(content=repair_prompt),
        HumanMessage(content=(
            f"BLUEPRINT CODE:\n{state['blueprint_code']}\n\n"
            f"CURRENT SUMMARY:\n{state['summary']}\n\n"
            f"FEEDBACK TO ADDRESS:\n{state['feedback']}\n\n"
            "Please provide the corrected and improved summary."
        ))
    ]
    
    response = llm.invoke(messages)
    return {
        "summary": response.content,
        "iteration_count": state.get("iteration_count", 1) + 1
    }

def should_continue(state: AgentState):
    """
    Conditional edge to decide whether to END or REPAIR.
    """
    if state.get("feedback") == "PASSED" or state.get("iteration_count", 0) >= 3:
        return END
    return "repairer"

def create_summarizer_agent():
    """
    Creates a LangGraph agent with a checker/repairer pattern.
    """
    workflow = StateGraph(AgentState)
    
    workflow.add_node("summarizer", summarize_blueprint_node)
    workflow.add_node("checker", check_summary_node)
    workflow.add_node("repairer", repair_summary_node)
    
    workflow.set_entry_point("summarizer")
    
    workflow.add_edge("summarizer", "checker")
    
    workflow.add_conditional_edges(
        "checker",
        should_continue,
        {
            END: END,
            "repairer": "repairer"
        }
    )
    
    workflow.add_edge("repairer", "checker")
    
    return workflow.compile()
