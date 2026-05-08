import random
from mcp_server.mcp_server import SessionLocal
from sqlalchemy import text

# Realistic Indian/Common Names for the Fintech feel
first_names = ["Arjun", "Deepak", "Ishani", "Kabir", "Meera", "Rahul", "Sana", "Vikram", "Yash", "Zoya", "Rohan", "Priya", "Amit", "Sneha", "Karan"]
last_names = ["Sharma", "Verma", "Gupta", "Malhotra", "Reddy", "Patel", "Khan", "Joshi", "Singh", "Nair"]

def generate_bulk_data(n=100):
    db = SessionLocal()
    print(f"🚀 Starting to seed {n} clients into the database...")
    
    try:
        for i in range(n):
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            income = random.randint(30000, 250000)
            
            # Logic to keep credit score realistic based on debt
            score = random.randint(300, 850)
            debt = random.randint(1000, 150000)
            defaults = random.choice([0, 0, 0, 0, 1, 2]) # Mostly 0 defaults
            utilization = round(random.uniform(5.0, 95.0), 1)

            query = text("""
                INSERT INTO client_financials 
                (full_name, annual_income, current_credit_score, active_loans_count, total_outstanding_debt, past_defaults_count, credit_utilization_percentage)
                VALUES (:name, :income, :score, :loans, :debt, :defaults, :util)
            """)
            
            db.execute(query, {
                "name": name,
                "income": income,
                "score": score,
                "loans": random.randint(0, 5),
                "debt": debt,
                "defaults": defaults,
                "util": utilization
            })
        
        db.commit()
        print(f"✅ Successfully added {n} new clients!")
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    generate_bulk_data(200)