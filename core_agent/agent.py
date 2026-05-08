import os
import logging
from typing import Annotated, TypedDict
from dotenv import load_dotenv

# LangChain & LangGraph Imports
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, BaseMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

# Importing the function directly from your Stage 2 MCP server
from mcp_server.mcp_server import get_client_financial_data

# 1. Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Check for API Key
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    logger.error("❌ GROQ_API_KEY is missing in .env file! Please check.")

# 2. Define the Tool
@tool
def fetch_client_data(client_id: int) -> str:
    """
    ALWAYS use this tool to fetch the financial profile of a client using their client_id.
    Do NOT guess or hallucinate the data. Fetch it first from the database.
    """
    logger.info(f"🤖 Agent is using tool to fetch data for client: {client_id}")
    return get_client_financial_data(client_id)

tools = [fetch_client_data]

# 3. Define Agent State
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# 4. System Prompt
SYSTEM_PROMPT = """You are an expert, highly analytical Credit Score Analyst.
Your job is to generate a formal, professional Credit Memo for clients based on real data.

Follow these strict steps:
1. You will receive a request containing a Client ID.
2. YOU MUST USE YOUR TOOL 'fetch_client_data' to get the real financial data for that ID. 
3. Analyze their risk based on income vs. debt, past defaults, and credit utilization.
4. Generate a formal Credit Memo with EXACTLY these 3 sections:
   - **Executive Summary:** Brief overview of the client and their income.
   - **Risk Assessment:** Highlight any defaults, high utilization, or positive financial behaviors.
   - **Final Recommendation:** Clearly state whether a new loan should be APPROVED, REJECTED, or requires MANUAL REVIEW, and explain why.

Do not include any conversational filler. Output the memo directly in Markdown.
"""

llm = ChatGroq(
    model="llama-3.3-70b-versatile",  
    api_key=api_key,
    temperature=0.1
)

llm_with_tools = llm.bind_tools(tools)

# 6. Define Graph Nodes
def chatbot_node(state: AgentState):
    messages_for_llm = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    logger.info("🧠 LLM is thinking and analyzing...")
    response = llm_with_tools.invoke(messages_for_llm)
    return {"messages": [response]}

# 7. Build the LangGraph
graph_builder = StateGraph(AgentState)
graph_builder.add_node("chatbot", chatbot_node)
graph_builder.add_node("tools", ToolNode(tools=tools))
graph_builder.add_edge(START, "chatbot")

graph_builder.add_conditional_edges(
    "chatbot",
    lambda state: "tools" if state["messages"][-1].tool_calls else END,
)
graph_builder.add_edge("tools", "chatbot")

# Compile the Graph
credit_agent = graph_builder.compile()
logger.info("✅ LangGraph Agent Core Compiled successfully (Powered by Groq)!")