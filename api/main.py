import logging
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from core_agent.agent import credit_agent
from mcp_server.mcp_server import SessionLocal # Direct session use kar rahe hain
from sqlalchemy import text

# 1. Setup Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Credit Analyst API", version="2.0")

# 2. Schema Models
class CreditRequest(BaseModel):
    client_id: int

class CreditResponse(BaseModel):
    client_id: int
    memo: str
    metrics: dict  # Raw numbers for the frontend boxes

# 3. New Endpoint: Fetch All Clients for Dropdown
@app.get("/clients")
async def get_clients():
    db = SessionLocal()
    try:
        # Fetching names and IDs for the dropdown
        query = text("SELECT client_id, full_name FROM client_financials ORDER BY client_id ASC")
        result = db.execute(query).mappings().all()
        return [{"id": r["client_id"], "name": r["full_name"]} for r in result]
    except Exception as e:
        logger.error(f"❌ DB Error in /clients: {e}")
        raise HTTPException(status_code=500, detail="Could not fetch clients list")
    finally:
        db.close()

# 4. Updated Analyze Endpoint
@app.post("/analyze", response_model=CreditResponse)
async def analyze_client(request: CreditRequest):
    logger.info(f"📬 API Request: Analyzing Client ID {request.client_id}")
    db = SessionLocal()
    try:
        # First: Fetch raw data for the Metric Boxes
        query = text("SELECT * FROM client_financials WHERE client_id = :cid")
        raw_data = db.execute(query, {"cid": request.client_id}).mappings().first()
        
        if not raw_data:
            raise HTTPException(status_code=404, detail="Client not found")

        # Second: Trigger LangGraph Agent for Memo
        user_input = f"Write a credit memo for client ID {request.client_id}"
        inputs = {"messages": [HumanMessage(content=user_input)]}
        result = await credit_agent.ainvoke(inputs)
        final_memo = result["messages"][-1].content

        return CreditResponse(
            client_id=request.client_id,
            memo=final_memo,
            metrics={
                "score": raw_data["current_credit_score"],
                "utilization": float(raw_data["credit_utilization_percentage"]),
                "income": float(raw_data["annual_income"]),
                "debt": float(raw_data["total_outstanding_debt"])
            }
        )
    except Exception as e:
        logger.error(f"❌ API Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()