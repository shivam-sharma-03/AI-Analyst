import os
import logging
from typing import List
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Float, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Configure professional logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "credit_db")

# Connection strings
DEFAULT_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres"
TARGET_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

Base = declarative_base()

class ClientFinancial(Base):
    """Client Financial Data Model"""
    __tablename__ = "client_financials"

    client_id = Column(Integer, primary_key=True, autoincrement=True)  # ✅ Changed to True
    full_name = Column(String, nullable=False)
    annual_income = Column(Float, nullable=False)
    current_credit_score = Column(Integer, nullable=False)
    active_loans_count = Column(Integer, nullable=False)
    total_outstanding_debt = Column(Float, nullable=False)
    past_defaults_count = Column(Integer, nullable=False)
    credit_utilization_percentage = Column(Float, nullable=False)
    
    def to_dict(self) -> dict:
        """✅ Added: Convert to dictionary for JSON serialization"""
        return {
            "client_id": self.client_id,
            "full_name": self.full_name,
            "annual_income": self.annual_income,
            "current_credit_score": self.current_credit_score,
            "active_loans_count": self.active_loans_count,
            "total_outstanding_debt": self.total_outstanding_debt,
            "past_defaults_count": self.past_defaults_count,
            "credit_utilization_percentage": self.credit_utilization_percentage
        }
    
    def __repr__(self) -> str:
        return f"<ClientFinancial(id={self.client_id}, name='{self.full_name}', score={self.current_credit_score})>"

def create_database_if_not_exists():
    """Creates the target database if it doesn't already exist."""
    try:
        engine = create_engine(DEFAULT_DATABASE_URL, isolation_level="AUTOCOMMIT")
        with engine.connect() as conn:
            # Check if database exists
            result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'"))
            if not result.scalar():
                logger.info(f"🔨 Database '{DB_NAME}' not found. Creating it...")
                conn.execute(text(f"CREATE DATABASE {DB_NAME}"))
                logger.info(f"✅ Database '{DB_NAME}' created successfully.")
            else:
                logger.info(f"✅ Database '{DB_NAME}' already exists.")
        engine.dispose()
    except SQLAlchemyError as e:
        logger.error(f"❌ Error checking/creating database: {e}")
        raise

def get_dummy_data() -> List[dict]:
    """Returns a list of 10 distinct client profiles (IDs removed for autoincrement)."""
    return [
        # --- GOOD PROFILES (3) ---
        {"full_name": "Aarav Patel", "annual_income": 120000.0, "current_credit_score": 780, "active_loans_count": 1, "total_outstanding_debt": 15000.0, "past_defaults_count": 0, "credit_utilization_percentage": 12.5},
        {"full_name": "Neha Sharma", "annual_income": 95000.0, "current_credit_score": 810, "active_loans_count": 0, "total_outstanding_debt": 2000.0, "past_defaults_count": 0, "credit_utilization_percentage": 5.0},
        {"full_name": "Rohan Gupta", "annual_income": 200000.0, "current_credit_score": 760, "active_loans_count": 2, "total_outstanding_debt": 45000.0, "past_defaults_count": 0, "credit_utilization_percentage": 20.0},
        
        # --- AVERAGE PROFILES (4) ---
        {"full_name": "Priya Singh", "annual_income": 65000.0, "current_credit_score": 680, "active_loans_count": 2, "total_outstanding_debt": 25000.0, "past_defaults_count": 1, "credit_utilization_percentage": 45.0},
        {"full_name": "Vikram Desai", "annual_income": 80000.0, "current_credit_score": 695, "active_loans_count": 1, "total_outstanding_debt": 18000.0, "past_defaults_count": 0, "credit_utilization_percentage": 55.0},
        {"full_name": "Ananya Reddy", "annual_income": 55000.0, "current_credit_score": 650, "active_loans_count": 3, "total_outstanding_debt": 30000.0, "past_defaults_count": 0, "credit_utilization_percentage": 60.0},
        {"full_name": "Karan Malhotra", "annual_income": 110000.0, "current_credit_score": 710, "active_loans_count": 4, "total_outstanding_debt": 60000.0, "past_defaults_count": 1, "credit_utilization_percentage": 35.0},
        
        # --- HIGH-RISK PROFILES (3) ---
        {"full_name": "Sneha Iyer", "annual_income": 45000.0, "current_credit_score": 540, "active_loans_count": 5, "total_outstanding_debt": 40000.0, "past_defaults_count": 3, "credit_utilization_percentage": 85.0},
        {"full_name": "Amit Kumar", "annual_income": 35000.0, "current_credit_score": 490, "active_loans_count": 2, "total_outstanding_debt": 25000.0, "past_defaults_count": 4, "credit_utilization_percentage": 95.0},
        {"full_name": "Pooja Verma", "annual_income": 70000.0, "current_credit_score": 580, "active_loans_count": 6, "total_outstanding_debt": 80000.0, "past_defaults_count": 2, "credit_utilization_percentage": 78.0},
    ]

def seed_database():
    """Creates tables and inserts the dummy data with verification."""
    engine = create_engine(TARGET_DATABASE_URL, echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = SessionLocal()
    
    try:
        # Recreate tables from scratch for a clean slate
        logger.info("🗑️  Dropping existing tables (if any)...")
        Base.metadata.drop_all(bind=engine)
        
        logger.info("🔨 Creating tables...")
        Base.metadata.create_all(bind=engine)
        
        clients_data = get_dummy_data()
        clients_to_insert = [ClientFinancial(**data) for data in clients_data]
        
        logger.info(f"📥 Inserting {len(clients_to_insert)} records into 'client_financials' table...")
        db_session.bulk_save_objects(clients_to_insert)
        db_session.commit()
        
        # ✅ VERIFICATION STEP
        logger.info("🔍 Verifying inserted data...")
        count = db_session.query(ClientFinancial).count()
        logger.info(f"📊 Total records in database: {count}")
        
        if count == 10:
            logger.info("✅ All 10 records inserted successfully!")
            
            # Show summary by risk category
            good = db_session.query(ClientFinancial).filter(ClientFinancial.current_credit_score >= 750).count()
            avg = db_session.query(ClientFinancial).filter(
                ClientFinancial.current_credit_score >= 650,
                ClientFinancial.current_credit_score < 750
            ).count()
            high_risk = db_session.query(ClientFinancial).filter(ClientFinancial.current_credit_score < 650).count()
            
            logger.info(f"   🟢 Good Credit (750+): {good}")
            logger.info(f"   🟡 Average Credit (650-749): {avg}")
            logger.info(f"   🔴 High-Risk (<650): {high_risk}")
            
            # Sample preview
            logger.info("\n📋 Sample Records:")
            samples = db_session.query(ClientFinancial).limit(3).all()
            for client in samples:
                logger.info(f"   • {client}")
        else:
            logger.warning(f"⚠️  Expected 10 records but found {count}")
        
        logger.info("\n✅ Database seeded successfully!")
        logger.info(f"🔗 Connection: postgresql://{DB_USER}:****@{DB_HOST}:{DB_PORT}/{DB_NAME}")
        
    except SQLAlchemyError as e:
        logger.error(f"❌ Database operation failed: {e}")
        db_session.rollback()
        raise
    finally:
        db_session.close()
        engine.dispose()

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🚀 Starting Stage 1: Database Setup and Seeding")
    logger.info("=" * 60)
    
    create_database_if_not_exists()
    seed_database()
    
    logger.info("=" * 60)
    logger.info("✅ Stage 1 Complete!")
    logger.info("=" * 60)
    logger.info("\n💡 Next Steps:")
    logger.info("   1. Verify: psql -U postgres -d credit_db -c 'SELECT * FROM client_financials;'")
    logger.info("   2. Start Stage 2: Build FastMCP Server")