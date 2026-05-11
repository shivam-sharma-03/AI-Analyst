# core_agent/policy.py

def check_user_permission(user_id: str, client_id: int) -> dict:
    """
    Simulates a Policy Enforcement Engine (RBAC).
    Checks if the given employee ID has access to run analysis.
    """
    if not user_id:
        return {"status": "denied", "reason": "User ID missing. Authentication required."}
    
    # core_agent/policy.py
    authorized_employees = ["E102938", "ADMIN01", "ANALYST_X", "DASHBOARD_USER"]
    
    if user_id.upper() not in authorized_employees:
        return {
            "status": "denied", 
            "reason": f"Employee {user_id} is not authorized to generate memos."
        }
        
    return {"status": "approved", "reason": "Clearance granted."}