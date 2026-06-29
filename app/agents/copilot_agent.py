import json
import re
from typing import TypedDict
from langgraph.graph import StateGraph, END
from app.services.llm_service import llm_service
from app.tools import query_knowledge_base, query_database, send_email

class AgentState(TypedDict):
    question: str
    history: list[dict]
    thought_log: list[str]
    next_tool: str | None
    next_tool_args: dict | None
    final_answer: str | None

# Map tool names to actual functions
TOOLS = {
    "query_knowledge_base": query_knowledge_base,
    "query_database": query_database,
    "send_email": send_email
}

def agent_node(state: AgentState) -> dict:
    history_str = ""
    for h in state.get("history", []):
        role = h.get("role", "User")
        content = h.get("content", "")
        history_str += f"{role}: {content}\n"
    
    thought_str = ""
    for t in state.get("thought_log", []):
        thought_str += f"{t}\n"
        
    prompt = f"""You are an Enterprise AI Copilot agent. You help users by querying the knowledge base, executing read-only database queries, and sending emails.

You have access to the following tools:
1. query_knowledge_base: Search the knowledge base for document contents (policies, specs, uploaded PDFs).
   Usage: Action: query_knowledge_base
          Action Input: {{"query": "search query"}}
2. query_database: Execute read-only SELECT database queries.
   Usage: Action: query_database
          Action Input: {{"sql_query": "SELECT ..."}}
3. send_email: Send mock email to a user.
   Usage: Action: send_email
          Action Input: {{"recipient": "user@example.com", "subject": "subject", "body": "email body"}}

You must respond in one of two formats:

Format A (If you need to use a tool):
Action: tool_name
Action Input: {{"arg_name": "arg_value"}}

Format B (If you have the final answer):
Final Answer: your detailed response

Here is the conversation history:
{history_str}
Here are your previous thoughts and tool outputs in this session:
{thought_str}
User Question: {state['question']}

Think step-by-step. Choose the appropriate format. Do not write anything after the format structure.
"""
    output = llm_service.generate(prompt).strip()
    
    # Parse output for tools
    action_match = re.search(r"Action:\s*(\w+)", output)
    action_input_match = re.search(r"Action Input:\s*(\{.*\})", output, re.DOTALL)
    
    if action_match and action_input_match:
        tool_name = action_match.group(1).strip()
        tool_args_str = action_input_match.group(1).strip()
        try:
            tool_args = json.loads(tool_args_str)
            return {
                "thought_log": state.get("thought_log", []) + [output],
                "next_tool": tool_name,
                "next_tool_args": tool_args
            }
        except Exception:
            pass
            
    # Default to Final Answer if parsing fails or Final Answer is present
    final_match = re.search(r"Final Answer:\s*(.*)", output, re.DOTALL)
    answer = final_match.group(1).strip() if final_match else output
    
    return {
        "final_answer": answer,
        "next_tool": None,
        "next_tool_args": None
    }

def action_node(state: AgentState) -> dict:
    tool_name = state["next_tool"]
    tool_args = state["next_tool_args"]
    
    if not tool_name or tool_name not in TOOLS:
        return {
            "next_tool": None,
            "next_tool_args": None,
            "thought_log": state.get("thought_log", []) + [f"System: Invalid tool '{tool_name}'."]
        }
        
    tool_func = TOOLS[tool_name]
    try:
        # Invoke tool function
        result = tool_func.invoke(tool_args)
        tool_result_str = f"Tool output from '{tool_name}':\n{result}"
    except Exception as e:
        tool_result_str = f"Error executing '{tool_name}': {str(e)}"
        
    return {
        "next_tool": None,
        "next_tool_args": None,
        "thought_log": state.get("thought_log", []) + [tool_result_str]
    }

def should_continue(state: AgentState) -> str:
    # If the thought log has exceeded a limit (e.g. 5 steps), force termination to prevent loops
    if len(state.get("thought_log", [])) >= 10:
        return "end"
    if state.get("next_tool"):
        return "continue"
    return "end"

# Build the workflow graph
workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("action", action_node)

workflow.set_entry_point("agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "action",
        "end": END
    }
)
workflow.add_edge("action", "agent")

copilot_agent = workflow.compile()
