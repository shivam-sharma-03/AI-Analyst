# 🏦 Pro AI Agentic Credit Score Analyst

An end-to-end Financial Risk Assessment System powered by LangGraph, Groq (Llama-3.3-70B), and FastMCP.

![AI Credit Analyst Dashboard](image/dashboard.png) *

## 🌟 Overview
This project is a production-grade AI Agent designed for banks and fintech firms. It automates the generation of Professional Credit Memos by securely fetching real-time financial data from a PostgreSQL database using an MCP (Model Context Protocol) server and performing deep-dive reasoning using an Agentic Workflow.

### 🎯 What Makes This Special?
Unlike simple chatbots, this system uses **LangGraph** to create a stateful, tool-using agent:
* **🔍 Tool Use:** The agent identifies the need for data and automatically calls the `fetch_client_data` tool.
* **🔌 MCP Integration:** Uses FastMCP to safely bridge the gap between the LLM and the Database.
* **🧠 Reasoning:** Analyzes Debt-to-Income (DTI) ratios, Credit Utilization, and Risk History like a human analyst.
* **📄 Professional Output:** Generates a structured Markdown Credit Memo with Executive Summary, Risk Assessment, and Final Recommendations.

---

## 🏗️ Technical Architecture

```text
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