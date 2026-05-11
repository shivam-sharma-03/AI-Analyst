import streamlit as st
import requests

# 1. Page Config
st.set_page_config(page_title="AI Credit Analyst Pro", page_icon="🏦", layout="wide")

# 2. State Management
if "current_analysis" not in st.session_state:
    st.session_state.current_analysis = None

# Custom CSS for UI
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    [data-testid="stMetricValue"] { font-size: 32px; font-weight: bold; color: #1f77b4; }
    .stSelectbox div[data-baseweb="select"] { cursor: text; }
    .stDownloadButton>button { background-color: #28a745 !important; color: white !important; width: 100%; }
    </style>
""", unsafe_allow_html=True)

# 3. Sidebar: Analyst Controls & Security
st.sidebar.header("📋 Analyst Controls")

st.sidebar.markdown("### 🔐 Employee Access")
emp_id = st.sidebar.text_input("Enter Employee ID", type="password", help="Enter your authorized corporate ID")

# Check if ID is provided (Validation logic)
is_authenticated = False
if emp_id:
    # Note: In a real app, this would check against a JWT or DB, 
    # but for our current Governance logic, we pass it to the backend.
    is_authenticated = True
    st.sidebar.success(f"Access Identity: {emp_id}")
else:
    st.sidebar.warning("🔑 Please enter Employee ID to enable analysis.")

@st.cache_data(ttl=300)
def load_clients():
    try:
        # Backend service name 'backend' used for Docker networking
        r = requests.get("http://backend:8000/clients", timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        return []
    return []

client_list = load_clients()

target_id = None
if client_list:
    options_display = [f"{c['name']} (ID: {c['id']})" for c in client_list]
    id_mapping = {f"{c['name']} (ID: {c['id']})": c['id'] for c in client_list}
    
    selected_label = st.sidebar.selectbox(
        "🔍 Search or Select Client", 
        options=options_display,
        index=None,
        placeholder="Choose a client...",
        help="Type client name or ID to filter"
    )
    
    target_id = id_mapping[selected_label] if selected_label else None
else:
    st.sidebar.error("⚠️ Backend Offline: Could not load client list.")

# Button Logic: Only enabled if Client is selected AND Employee ID is entered
analyze_btn = st.sidebar.button(
    "🚀 Run AI Analysis", 
    disabled=(target_id is None or not is_authenticated),
    help="Requires Client Selection and Employee ID"
)

# 4. UI Header
st.title("🏦 Pro AI Credit Analyst")
st.markdown("### Automated Financial Risk Assessment System")
st.divider()

# 5. Analysis Execution
if analyze_btn:
    with st.spinner(f"🧠 Agent is performing deep-dive analysis for ID {target_id}..."):
        try:
            # Passing both client_id and emp_id as per our new Main.py schema
            payload = {
                "client_id": target_id,
                "emp_id": emp_id
            }
            res = requests.post("http://backend:8000/analyze", json=payload, timeout=60)
            
            if res.status_code == 200:
                st.session_state.current_analysis = res.json()
                st.success("✅ Analysis Updated!")
            elif res.status_code == 403:
                # Proper handling of Policy/Governance Denial
                st.session_state.current_analysis = None
                st.error(f"🚫 Permission Denied: {res.json().get('detail', 'Unauthorized Access')}")
            elif res.status_code == 404:
                st.error("❌ Client data not found in records.")
            else:
                st.error(f"❌ API Error: {res.json().get('detail', 'Unknown error')}")
        except Exception as e:
            st.error("❌ Connection Failed: Is the FastAPI backend running?")

# 6. Result Display
if st.session_state.current_analysis:
    data = st.session_state.current_analysis
    m = data["metrics"]
    
    # Financial Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Credit Score", m["score"], 
               delta="Healthy" if m["score"] > 700 else "Critical", 
               delta_color="normal" if m["score"] > 700 else "inverse")
    
    col2.metric("Utilization", f"{m['utilization']}%", 
               delta="Safe" if m["utilization"] < 30 else "Excessive", 
               delta_color="inverse")
    
    col3.metric("Annual Income", f"${m['income']:,.0f}")
    col4.metric("Total Debt", f"${m['debt']:,.0f}")

    st.markdown("---")
    st.subheader("📄 Credit Memo: Automated Final Report")
    
    # The Markdown Analysis Text from Agent
    st.markdown(data["memo"])
    
    # Action Row
    st.divider()
    c1, c2 = st.columns([1, 3])
    with c1:
        st.download_button(
            label="📥 Download Memo",
            data=data["memo"].encode('utf-8'),
            file_name=f"Credit_Memo_Client_{target_id}.md",
            mime="text/markdown",
            key="dl_final"
        )
else:
    # Welcome / Instruction state
    if not is_authenticated:
        st.info("👈 Please enter your **Employee ID** in the sidebar to begin.")
    elif target_id is None:
        st.info("👈 Select a **Client** from the dropdown to run the risk assessment.")