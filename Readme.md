🏦 Pro AI Agentic Credit Score Analyst
<div align="center">
An end-to-end Financial Risk Assessment System powered by LangGraph, Groq (Llama-3.3-70B), and FastMCP.
</div>

🌟 Overview
This project is a production-grade AI Agent designed for banks and fintech firms. It automates the generation of Credit Memos by securely fetching real-time financial data from a PostgreSQL database using an MCP (Model Context Protocol) server and performing deep-dive reasoning using an Agentic Workflow.
🎯 What Makes This Special?
Unlike simple chatbots, this system uses LangGraph to create a stateful, tool-using agent:

🔍 Tool Use: The agent identifies the need for data and calls the fetch_client_data tool
🔌 MCP Integration: Uses FastMCP to bridge the gap between the LLM and the Database
🧠 Reasoning: Analyzes Debt-to-Income (DTI) ratios, Credit Utilization, and Risk History
📄 Professional Output: Generates a structured Markdown Credit Memo with:

Executive Summary
Risk Assessment
Final Recommendation (APPROVED/REJECTED/MANUAL REVIEW)




🏗️ Technical Architecture
┌─────────────────┐
│   Streamlit UI  │
│  (Frontend)     │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   FastAPI       │
│  (REST API)     │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   LangGraph     │
│  Agent Core     │
└────────┬────────┘
         │
    ┌────┴────┐
    ↓         ↓
┌────────┐  ┌──────────┐
│  Groq  │  │ FastMCP  │
│ LLM    │  │  Server  │
└────────┘  └─────┬────┘
                  ↓
            ┌──────────┐
            │PostgreSQL│
            └──────────┘
🛠️ Tech Stack
ComponentTechnologyFrontendStreamlit (Searchable Dashboard with Session Persistence)API LayerFastAPI (Asynchronous endpoints with Pydantic validation)Agent OrchestrationLangGraph (Stateful graph with ToolNode)LLM InferenceGroq - Llama-3.3-70B-Versatile (Ultra-fast reasoning)Database BridgeFastMCP (Model Context Protocol)DatabasePostgreSQL (Client financial records)

🚀 Getting Started
1️⃣ Prerequisites

Python 3.10+
PostgreSQL (with a database set up)
Groq API Key (Get it here)

2️⃣ Environment Setup
Create a .env file in the root directory:
env# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/your_db_name

# API Keys
GROQ_API_KEY=your_groq_api_key_here
3️⃣ Installation
bash# Clone the repository
git clone <your-repo-url>
cd credit_score_agent

# Create Virtual Environment
python -m venv .venv

# Activate Virtual Environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install Dependencies
pip install -r requirements.txt
4️⃣ Database Setup
Make sure you have a PostgreSQL database with a clients table containing financial data. Example schema:
sqlCREATE TABLE clients (
    client_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    income DECIMAL(10, 2),
    total_debt DECIMAL(10, 2),
    credit_score INT,
    credit_utilization DECIMAL(5, 2),
    past_defaults INT,
    loan_amount DECIMAL(10, 2)
);
5️⃣ Running the System
You need to run two services simultaneously:
Terminal 1️⃣ (Backend API):
bashuvicorn api.main:app --reload
✅ API will be available at: http://localhost:8000
Terminal 2️⃣ (Frontend Dashboard):
bashstreamlit run frontend/app.py
✅ Dashboard will open at: http://localhost:8501

📁 Project Structure
credit_score_agent/
│
├── core_agent/
│   ├── __init__.py
│   └── agent.py              # LangGraph Agent Logic
│
├── mcp_server/
│   ├── __init__.py
│   └── mcp_server.py         # FastMCP Database Bridge
│
├── api/
│   ├── __init__.py
│   └── main.py               # FastAPI Endpoints
│
├── frontend/
│   └── app.py                # Streamlit Dashboard
│
├── test_agent.py             # Standalone Agent Test
├── .env                      # Environment Variables
├── requirements.txt          # Python Dependencies
└── README.md                 # This File

🎨 Key Features
✨ Frontend (Streamlit)

🔍 Searchable Client Selection: Type-to-filter dropdown for 100+ clients
📊 Real-time Financial Metrics: Instant visual boxes for Credit Score, Utilization, and Income
💾 Persistent Sessions: State-managed UI ensures data stays visible after downloading reports
📥 Exportable Reports: Download the professional Credit Memo as a .md file

🤖 Agent Capabilities

Tool Calling: Automatically decides when to fetch data
Risk Analysis: Evaluates DTI ratio, credit utilization, and default history
Professional Memo Generation: Structured output with clear recommendations

⚡ Performance

Groq Inference: Sub-second response times
Async API: Non-blocking FastAPI endpoints
MCP Protocol: Efficient database queries


🧪 Testing
Test the Agent Directly (Without UI):
bashpython test_agent.py
This will generate a Credit Memo for Client ID 1 and print it in the terminal.

📊 Example Output
markdown# Credit Memo - Client Analysis

## Executive Summary
**Client Name:** Aarav Patel  
**Monthly Income:** ₹75,000  
**Credit Score:** 720  
**Requested Loan Amount:** ₹50,000

## Risk Assessment
- **Credit Utilization:** 25% (Healthy)
- **Debt-to-Income Ratio:** 40% (Moderate)
- **Past Defaults:** 0 (Excellent)
- **Financial Stability:** Strong income with low utilization

## Final Recommendation
✅ **APPROVED**

The client demonstrates strong financial discipline with a high credit score, 
zero defaults, and manageable debt levels. Recommended for approval with 
standard interest rates.

🔧 Troubleshooting
Issue: Model Decommissioned Error
Error: llama3-8b-8192 has been decommissioned
Fix: Update core_agent/agent.py line 61:
pythonllm = ChatGroq(
    model="llama-3.3-70b-versatile",  # Use this instead
    api_key=api_key,
    temperature=0.1
)
Issue: Database Connection Error
Fix: Verify your .env file has the correct DATABASE_URL
Issue: Missing API Key
Fix: Make sure GROQ_API_KEY is set in your .env file

🛣️ Roadmap

 Add multi-currency support
 Implement credit score prediction model
 Add PDF export for Credit Memos
 Deploy on cloud (AWS/GCP)
 Add user authentication
 Create admin dashboard for bulk analysis


👨‍💻 Developed By
Shivam Sharma
Founder, Shivam Web Development
Show Image
Show Image

📝 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments

LangChain & LangGraph for the agent framework
Groq for lightning-fast LLM inference
Anthropic for MCP protocol standards
Streamlit for rapid UI development


<div align="center">
⭐ Star this repo if you found it helpful!
Made with ❤️ and ☕ in India
</div>

Ab requirements.txt bhi banao:
Create karo requirements.txt file:
txt# Core Framework
fastapi==0.115.0
uvicorn[standard]==0.32.0
streamlit==1.39.0

# LangChain & LangGraph
langchain-groq==0.2.0
langchain-core==0.3.0
langgraph==0.2.0

# Database
psycopg2-binary==2.9.9
sqlalchemy==2.0.36

# MCP
mcp==1.0.0

# Utilities
python-dotenv==1.0.1
requests==2.32.3
pydantic==2.9.0

# Optional (for enhanced features)
pandas==2.2.0

Final Steps:

Root folder mein 2 files banao:

README.md (upar wala full content)
requirements.txt (dependencies list)


Git push karne se pehle:

bash   git add README.md requirements.txt
   git commit -m "Added professional README and requirements"
   git push