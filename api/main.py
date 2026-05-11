import os
import time
import re
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

# LangChain and Core Logic Imports
from langchain_core.messages import HumanMessage
from core_agent.policy import check_user_permission
from core_agent.agent import credit_agent 

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# --- 1. ENTERPRISE LOGGING SETUP ---
class UserLogFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, 'user_id'):
            record.user_id = 'SYSTEM'
        return True

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(user_id)s] - %(message)s')
logger = logging.getLogger("EnterpriseAPI")
logger.addFilter(UserLogFilter())

app = FastAPI(title="Pro AI Agentic API - Enterprise Edition")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. DATABASE HELPER ---
def execute_db(query: str, params: tuple = (), is_write: bool = False):
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, params)
        if is_write:
            conn.commit()
            return {"status": "success"}
        data = cursor.fetchall() if cursor.description else []
        cursor.close()
        return data
    except Exception as e:
        if conn: conn.rollback()
        logger.error(f"❌ DB Error: {e}")
        raise HTTPException(status_code=500, detail="Database operation failed.")
    finally:
        if conn: conn.close()

# --- 3. SCHEMAS (Jira US-5 & Dashboard) ---
class OpenAIMessage(BaseModel):
    role: str
    content: str

class OpenAIRequest(BaseModel):
    model: str
    messages: List[OpenAIMessage]
    user: Optional[str] = "ANONYMOUS"
    stream: Optional[bool] = False

class CreditRequest(BaseModel):
    client_id: int
    emp_id: str  # Dynamic Employee ID from Dashboard

class MetricsResponse(BaseModel):
    score: int
    utilization: float
    income: float
    debt: float

class CreditResponse(BaseModel):
    client_id: int
    memo: str
    metrics: MetricsResponse

# --- 4. OPENAI COMPATIBLE ENDPOINT (Jira US-5) ---
@app.post("/v1/chat/completions")
async def chat_completions(req: OpenAIRequest):
    user_id = req.user if req.user else "UNKNOWN_EMP"
    user_msg = req.messages[-1].content
    
    # ID Extraction via Regex
    match = re.search(r'(?:client|id|ID|case)\s*[:#]?\s*(\d+)', user_msg, re.IGNORECASE)
    if not match:
        raise HTTPException(status_code=400, detail="Pattern match failed: Case ID/Client ID required.")
    client_id = int(match.group(1))

    # Policy Enforcement (Governance Check)
    policy = check_user_permission(user_id, client_id)
    if policy["status"] == "denied":
        logger.warning(f"🚫 Access Denied", extra={"user_id": user_id})
        raise HTTPException(status_code=403, detail=policy["reason"])

    try:
        logger.info(f"🤖 OpenAI Call: Starting Analysis for Client {client_id}", extra={"user_id": user_id})
        response = await credit_agent.ainvoke({
            "client_id": client_id,
            "user_info": {"employee_id": user_id},
            "messages": [HumanMessage(content=user_msg)]
        })
        
        return {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": req.model,
            "choices": [{"index": 0, "message": {"role": "assistant", "content": response["final_memo"]}, "finish_reason": "stop"}],
            "usage": {"total_tokens": 0} 
        }
    except Exception as e:
        logger.error(f"❌ Agent Crash: {str(e)}", extra={"user_id": user_id})
        raise HTTPException(status_code=500, detail="Agent internal error.")

# --- 5. DASHBOARD UI ENDPOINT (Jira US-3 & US-4) ---
@app.post("/analyze", response_model=CreditResponse)
async def analyze_client(request: CreditRequest):
    user_id = request.emp_id if request.emp_id else "DASHBOARD_USER"
    logger.info(f"📬 Dashboard Request: Client ID {request.client_id} by {user_id}", extra={"user_id": user_id})
    
    try:
        # 🛡️ Governance Check FIRST (Don't leak data if unauthorized)
        policy = check_user_permission(user_id, request.client_id)
        if policy["status"] == "denied":
            logger.warning(f"🚫 Security Alert: Unauthorized access attempt by {user_id}", extra={"user_id": user_id})
            raise HTTPException(status_code=403, detail=policy["reason"])

        # Fetch Financial Metrics
        query = "SELECT current_credit_score, credit_utilization_percentage, annual_income, total_outstanding_debt FROM client_financials WHERE client_id = %s"
        raw_data = execute_db(query, (request.client_id,))
        if not raw_data:
            raise HTTPException(status_code=404, detail="Client not found")
        data = raw_data[0]

        # Trigger Governed Agent Workflow
        response = await credit_agent.ainvoke({
            "client_id": request.client_id,
            "user_info": {"employee_id": user_id}
        })

        return CreditResponse(
            client_id=request.client_id,
            memo=response["final_memo"],
            metrics=MetricsResponse(
                score=int(data["current_credit_score"]),
                utilization=float(data["credit_utilization_percentage"]),
                income=float(data["annual_income"]),
                debt=float(data["total_outstanding_debt"])
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Dashboard Error: {str(e)}", extra={"user_id": user_id})
        raise HTTPException(status_code=500, detail="Dashboard analysis failed.")

# --- 6. UTILITY & HEALTH ENDPOINTS (Jira US-6/7 Readiness) ---
@app.get("/clients")
async def get_clients():
    result = execute_db("SELECT client_id, full_name FROM client_financials ORDER BY client_id ASC")
    return [{"id": r["client_id"], "name": r["full_name"]} for r in result]

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/ready")
async def readiness_check():
    try:
        execute_db("SELECT 1")
        return {"status": "ready"}
    except:
        raise HTTPException(status_code=503, detail="Database not reachable")