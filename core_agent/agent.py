import os
import logging
from typing import Annotated, TypedDict, List
from dotenv import load_dotenv

# LangChain & LangGraph
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, BaseMessage, HumanMessage
from langgraph.graph import StateGraph, START, END

# Imports from your modules
from mcp_server.mcp_server import get_client_financial_data
from core_agent.policy import check_user_permission

# 1. Setup Logging
logger = logging.getLogger("EnterpriseAgent")

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

# 2. Define Enterprise State
class AgentState(TypedDict):
    messages: List[BaseMessage]
    client_id: int
    user_info: dict
    client_data: str
    final_memo: str
    status: str  # approved/denied/submitted

# 3. Initialize LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=api_key,
    temperature=0.1
)

# --- NODES (Jira US-3, US-4 Requirements) ---

# Node 1: Validation (Identity & Policy Resolution)
def validation_node(state: AgentState):
    user_id = state.get("user_info", {}).get("employee_id", "GUEST")
    client_id = state["client_id"]
    
    logger.info(f"🛡️ Validating access for User: {user_id} on Client: {client_id}")
    check = check_user_permission(user_id, client_id)
    
    if check["status"] == "denied":
        error_msg = f"Policy Violation: {check['reason']}"
        return {"status": "denied", "final_memo": error_msg}
    
    return {"status": "approved"}

# Node 2: Fetch Data (US-2: MCP Tools Integration)
def fetch_data_node(state: AgentState):
    if state["status"] == "denied": return state
    
    client_id = state["client_id"]
    logger.info(f"🔌 MCP: Fetching real-time data for ID {client_id}")
    
    # Direct tool call logic (No more guessing)
    data = get_client_financial_data(client_id)
    return {"client_data": data}

# Node 3: Writing (US-4: Managed Reasoning)
def writing_node(state: AgentState):
    if state["status"] == "denied": return state
    
    logger.info("🧠 LLM: Analyzing and generating Credit Memo...")
    system_prompt = "You are a Senior Credit Analyst. Create a formal Markdown Credit Memo (Executive Summary, Risk Assessment, Final Recommendation) using this data: " + state["client_data"]
    
    response = llm.invoke([SystemMessage(content=system_prompt)])
    return {"final_memo": response.content, "messages": [response]}

# Node 4: Submission (US-3: Write/Audit Trail)
def submission_node(state: AgentState):
    if state["status"] == "denied": return state
    
    client_id = state["client_id"]
    user_id = state.get("user_info", {}).get("employee_id", "GUEST")
    
    # Yahan hum simulate kar rahe hain database mein "Analysis Status" update karna
    logger.info(f"📝 US-3: Logging final decision for Client {client_id} to Audit Table by {user_id}")
    
    # In real world: db.execute("INSERT INTO audit_logs ...")
    return {"status": "submitted"}

# --- 4. Build The Governed Graph (US-4: Strict Sequence) ---

builder = StateGraph(AgentState)

builder.add_node("validate", validation_node)
builder.add_node("fetch_data", fetch_data_node)
builder.add_node("write_memo", writing_node)
builder.add_node("submit_decision", submission_node)

# Strict Sequence Logic
builder.add_edge(START, "validate")
builder.add_edge("validate", "fetch_data")
builder.add_edge("fetch_data", "write_memo")
builder.add_edge("write_memo", "submit_decision")
builder.add_edge("submit_decision", END)

# Compile
credit_agent = builder.compile()
logger.info("✅ Enterprise Governed Agent Compiled!")