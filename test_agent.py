import logging
import os
from langchain_core.messages import HumanMessage, AIMessage  # Yahan AIMessage add kiya hai
from core_agent.agent import credit_agent

# Simple logging setup
logging.basicConfig(level=logging.INFO, format="%(message)s")

def test_run():
    print("🚀 Starting LangGraph Agent Test...\n")
    
    # We ask for ID 1 (Aarav Patel - Good Profile) or 10 (High Risk)
    user_input = "Write a credit memo for client ID 1"
    print(f"👤 User: {user_input}\n")
    print("-" * 50)
    
    inputs = {"messages": [HumanMessage(content=user_input)]}

    print(f"DEBUG: API Key exists: {bool(os.getenv('GROQ_API_KEY'))}")
    
    # Run the agent stream
    for event in credit_agent.stream(inputs, stream_mode="values"):
        message = event["messages"][-1]
        
        # FIX: Sirf AI (LLM) ke messages ko process karein
        if isinstance(message, AIMessage):
            
            # Print AI thoughts (Tool Calls)
            if message.tool_calls:
                print(f"🧠 Agent Logic: Using tool '{message.tool_calls[0]['name']}' with args {message.tool_calls[0]['args']}...")
            
            # Print final output (Jab tool call nahi hai aur content hai)
            elif message.content:
                print("\n📝 Final Credit Memo Generated:\n")
                print(message.content)
                
    print("\n" + "=" * 50)
    print("✅ Stage 3 Test Complete!")

if __name__ == "__main__":
    test_run()