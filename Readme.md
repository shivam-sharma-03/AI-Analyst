# 🏦 Pro AI Agentic Credit Score Analyst

An end-to-end Financial Risk Assessment System powered by LangGraph, Groq (Llama-3.3-70B), and FastMCP.

![AI Credit Analyst Dashboard](image/dashboard.png)

---

# 🌟 Overview

This project is a production-grade AI Agent designed for banks and fintech firms. It automates the generation of Professional Credit Memos by securely fetching real-time financial data from a PostgreSQL database using an MCP (Model Context Protocol) server and performing deep-dive reasoning using an Agentic Workflow.

## 🎯 What Makes This Special?

Unlike simple chatbots, this system uses **LangGraph** to create a stateful, tool-using agent:

- 🔍 **Tool Use:** The agent identifies the need for data and automatically calls the `fetch_client_data` tool.
- 🔌 **MCP Integration:** Uses FastMCP to safely bridge the gap between the LLM and the Database.
- 🧠 **Reasoning:** Analyzes Debt-to-Income (DTI) ratios, Credit Utilization, and Risk History like a human analyst.
- 📄 **Professional Output:** Generates a structured Markdown Credit Memo with Executive Summary, Risk Assessment, and Final Recommendations.

---

# 🏗️ Technical Architecture

```text
<<<<<<< HEAD
                                    ┌─────────────────┐
                                    │  Streamlit UI   │
                                    │   (Frontend)    │
                                    └────────┬────────┘
                                            │
                                            ↓
                                    ┌─────────────────┐
                                    │     FastAPI     │
                                    │   (REST API)    │
                                    └────────┬────────┘
                                            │
                                            ↓
                                    ┌─────────────────┐
                                    │    LangGraph    │
                                    │   Agent Core    │
                                    └────────┬────────┘
                                        ┌────┴────┐
                                        ↓         ↓
                                    ┌────────┐ ┌──────────┐
                                    │  Groq  │ │ FastMCP  │
                                    │  LLM   │ │  Server  │
                                    └────────┘ └─────┬────┘
                                                    ↓
                                                ┌──────────┐
                                                │PostgreSQL│
                                                └──────────┘
```
---

# 🛠️ Tech Stack

    | Component | Technology |
    |------------|-------------|
    | Frontend | Streamlit (Searchable Dashboard with Session Persistence) |
    | API Layer | FastAPI (Asynchronous endpoints with Pydantic validation) |
    | Agent Orchestration | LangGraph (Stateful graph with ToolNode) |
    | LLM Inference | Groq - Llama-3.3-70B-Versatile (Ultra-fast reasoning) |
    | Database Bridge | FastMCP (Model Context Protocol) |
    | Database | PostgreSQL (Client financial records) |
    | Containerization | Docker & Docker Compose |

---
# 🚀 Getting Started

### 1️⃣ Prerequisites

    - Python 3.10+
    - PostgreSQL (Running on your host machine)
    - Groq API Key
    - (Optional but recommended) Docker Desktop


### 2️⃣ Environment Setup

Create a `.env` file in the root directory.


If using Docker:
```
.env
    DB_USER=postgres
    DB_PASSWORD=your_password
    DB_HOST=host.docker.internal
    DATABASE_URL=postgresql://postgres:your_password@host.docker.internal:5432/credit_db
    DB_PORT=5432
    DB_NAME=credit_db
    GROQ_API_KEY=your_groq_api_key_here
```
⚠️ Note: If running WITHOUT Docker, change DB_HOST and DATABASE_URL host to localhost instead of host.docker.internal.

### 3️⃣ Database Seeding (Generate 200+ Clients)

Before running the app, populate your PostgreSQL database with realistic Fintech data:

    python scripts/seed_expanded_data.py

### 4️⃣ Running the System

#### Option A: The Docker Way 🐳 (Recommended)

If you have Docker installed, you can launch the entire infrastructure with a single command:

    docker-compose up --build
    ✅ Access URLs
    Dashboard → http://localhost:8501
    API → http://localhost:8000

#### Option B: The Manual Way 💻

If you don't have Docker, you can run the system natively using Python.

##### Step 1: Setup Virtual Environment & Install Dependencies
    python -m venv .venv

    # Activate on Windows
    .venv\Scripts\activate

    # Activate on macOS/Linux
    source .venv/bin/activate

    # Install required packages
    pip install -r requirements.txt

##### Step 2: Start the Backend (Terminal 1)

    uvicorn api.main:app --reload

##### Step 3: Start the Frontend (Terminal 2)
Open a new terminal, activate the virtual environment again, and run:

    streamlit run frontend/app.py

📁 Project Structure

    credit_score_agent/
    │
    ├── core_agent/
    │   └── agent.py                 # LangGraph Agent Logic
    │
    ├── mcp_server/
    │   └── mcp_server.py            # FastMCP Database Bridge
    │
    ├── api/
    │   └── main.py                  # FastAPI Endpoints
    │
    ├── frontend/
    │   └── app.py                   # Streamlit Dashboard
    │
    ├── scripts/
    │   └── seed_expanded_data.py    # Generates 200 dummy clients
    │
    ├── docker-compose.yml           # Orchestrates Backend & Frontend
    ├── Dockerfile                   # Container build instructions
    ├── .env                         # Environment Variables
    ├── requirements.txt             # Python Dependencies
    └── README.md                    # Project Documentation

🎨 Key Features

    ✨ Frontend (Streamlit)
    🔍 Searchable Client Selection: Type-to-filter dropdown for 200+ clients.
    📊 Real-time Financial Metrics: Instant visual boxes for Credit Score, Utilization, and Income.
    💾 Persistent Sessions: State-managed UI ensures data stays visible after downloading reports.
    📥 Exportable Reports: Download the professional Credit Memo as a .md file.
    🤖 Agent Capabilities
    ⚡ Tool Calling: Automatically decides when to fetch data via MCP.
    📉 Risk Analysis: Evaluates DTI ratio, credit utilization, and default history.
    🧾 Professional Memo Generation: Structured output with clear recommendations.

📌 Future Improvements

    Multi-agent financial review workflow
    PDF export support
    Real-time bank integrations
    Authentication & role-based access
    Cloud deployment (AWS/GCP/Azure)
