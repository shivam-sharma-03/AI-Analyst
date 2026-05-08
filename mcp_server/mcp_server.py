import os
import json
import logging
from fastmcp import FastMCP
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from decimal import Decimal
from datetime import date, datetime

# 1. Configure Professional Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 2. Load Environment Variables
load_dotenv()

# Fail-fast: Agar zaroori variables nahi hain toh default na le, rather none le aur hum check karein
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "credit_db")

if not all([DB_USER, DB_PASSWORD]):
    logger.warning("⚠️ DB_USER or DB_PASSWORD is not set in environment variables!")

TARGET_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 3. Setup Database Connection Engine
engine = create_engine(TARGET_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Initialize FastMCP Server
mcp = FastMCP("CreditAnalystDataServer")

# Custom JSON Encoder helper
def custom_json_serializer(obj):
    """Handles Decimal, Datetime, and Date objects for JSON serialization."""
    if isinstance(obj, (Decimal, date, datetime)):
        return str(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

# 5. Create and Expose the Tool
@mcp.tool()
def get_client_financial_data(client_id: int) -> str:
    """
    Fetches the complete financial profile of a client from the database using their client_id.
    This tool provides income, credit score, loan counts, debt, and credit utilization.
    Returns the data as a JSON string.
    """
    logger.info(f"🔍 Tool Called: get_client_financial_data for client_id={client_id}")
    db_session = SessionLocal()
    
    try:
        query = text("SELECT * FROM client_financials WHERE client_id = :client_id")
        result = db_session.execute(query, {"client_id": client_id}).mappings().first()

        if result:
            client_data = dict(result)
            logger.info(f"✅ Data found for client {client_id}")
            # Use default=custom_json_serializer to prevent crashes on Decimals/Dates
            return json.dumps(client_data, indent=2, default=custom_json_serializer)
        else:
            logger.warning(f"⚠️ No data found for client_id={client_id}")
            return json.dumps({"error": f"No financial data found for Client ID {client_id}. Please verify the ID."})
            
    except Exception as e:
        logger.error(f"❌ Database error while fetching client data: {e}", exc_info=True) # exc_info adds stack trace in logs
        return json.dumps({"error": "Internal database error occurred while fetching client data."})
    
    finally:
        db_session.close()

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🚀 Starting Stage 2: FastMCP Server")
    logger.info("=" * 60)
    
    mcp.run(transport="stdio")