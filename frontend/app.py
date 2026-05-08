import streamlit as st
import requests

# 1. Page Config
st.set_page_config(page_title="AI Credit Analyst Pro", page_icon="🏦", layout="wide")

# 2. State Management (Persistent Report)
if "current_analysis" not in st.session_state:
    st.session_state.current_analysis = None

# Custom CSS for a clean "Searchable" UI
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    [data-testid="stMetricValue"] { font-size: 32px; font-weight: bold; color: #1f77b4; }
    .stSelectbox div[data-baseweb="select"] { cursor: text; } /* Shows user they can type */
    .stDownloadButton>button { background-color: #28a745 !important; color: white !important; width: 100%; }
    </style>
""", unsafe_allow_html=True)

# 3. Sidebar: Load Clients List
st.sidebar.header("📋 Analyst Controls")

@st.cache_data(ttl=300) # Cache list for 5 minutes
def load_clients():
    try:
        r = requests.get("http://backend:8000/clients", timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        return []
    return []

client_list = load_clients()

if client_list:
    # 1. Sirf asli names ki list rakho, koi manual placeholder nahi
    options_display = [f"{c['name']} (ID: {c['id']})" for c in client_list]
    id_mapping = {f"{c['name']} (ID: {c['id']})": c['id'] for c in client_list}
    
    # 2. Native Placeholder logic
    selected_label = st.sidebar.selectbox(
        "🔍 Search or Select Client", 
        options=options_display,
        index=None,  # <--- Ye important hai! Isse default selection empty rahegi
        placeholder="Choose an option", # <--- Ye dikhega jab tak user kuch type na kare
        help="Type client name or ID to filter the list"
    )
    
    # target_id sirf tab assign hoga jab user koi item pick karega
    target_id = id_mapping[selected_label] if selected_label else None
else:
    st.sidebar.warning("⚠️ No clients found.")
    target_id = None

# Button tab tak disable rahega jab tak selection empty hai
analyze_btn = st.sidebar.button("🚀 Run AI Analysis", disabled=(target_id is None))

# 4. UI Header
st.title("🏦 Pro AI Credit Analyst")
st.markdown("### Automated Financial Risk Assessment System")
st.divider()

# 5. Analysis Execution
if analyze_btn:
    with st.spinner(f"🧠 Agent is performing deep-dive analysis for ID {target_id}..."):
        try:
            res = requests.post("http://backend:8000/analyze", json={"client_id": target_id}, timeout=60)
            if res.status_code == 200:
                st.session_state.current_analysis = res.json()
                st.success("✅ Analysis Updated!")
            else:
                st.error(f"❌ API Error: {res.json().get('detail', 'Unknown error')}")
        except Exception as e:
            st.error("❌ Connection Failed: Is FastAPI server running?")

# 6. Persistent Display (No refresh on download)
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
    st.subheader(f"📄 Credit Memo: {m.get('name', 'Final Report')}")
    
    # The Analysis Text
    st.markdown(data["memo"])
    
    # Action Row
    st.divider()
    c1, c2 = st.columns([1, 3])
    with c1:
        st.download_button(
            label="📥 Download Memo",
            data=data["memo"].encode('utf-8'),
            file_name=f"Credit_Memo_{target_id}.md",
            mime="text/markdown",
            key="dl_final"
        )
else:
    st.info("👈 Use the searchable dropdown in the sidebar to select a client.")