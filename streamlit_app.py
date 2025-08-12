#!/usr/bin/env python3
"""
CARE: Customer Assistance Resolution Engine
Simplified Streamlit App for Deployment
"""
import streamlit as st
import requests
import json
import time
import os
import threading
import sys
from datetime import datetime
from PIL import Image
from io import BytesIO
import plotly.express as px
import logging

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Add src to path
sys.path.append('src')

# Configure logging with proper file path
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/streamlit_app.log"),
        logging.StreamHandler()
    ]
)

# Page configuration
st.set_page_config(
    page_title="CARE: Customer Assistance Resolution Engine",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Environment setup
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:7860")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #0078d4 0%, #005a9e 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .customer-info {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 6px solid #0078d4;
        margin-bottom: 1.5rem;
    }
    .escalation-card {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_customer" not in st.session_state:
    st.session_state.selected_customer = None
if "backend_started" not in st.session_state:
    st.session_state.backend_started = False

def start_backend():
    """Start FastAPI backend if not running - optimized for speed"""
    if st.session_state.backend_started:
        return True
        
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=1)
        if response.status_code == 200:
            st.session_state.backend_started = True
            return True
    except:
        pass
    
    # Start backend in background
    try:
        # Ensure logs directory exists for backend too
        os.makedirs("logs", exist_ok=True)
        
        import uvicorn
        from fast_api import app
        
        def run_server():
            uvicorn.run(app, host="0.0.0.0", port=7860, log_level="error", workers=1)
        
        backend_thread = threading.Thread(target=run_server, daemon=True)
        backend_thread.start()
        time.sleep(2)  # Reduced wait time
        st.session_state.backend_started = True
        return True
    except Exception as e:
        logging.error(f"Failed to start backend: {e}")
        st.error(f"Failed to start backend: {e}")
        return False

@st.cache_data(ttl=60)  # Cache for 60 seconds
def get_customers():
    """Fetch customers from API with caching for speed"""
    try:
        response = requests.get(f"{API_BASE_URL}/customers", timeout=5)
        if response.status_code == 200:
            customers = response.json().get('customers', [])
            return customers
        else:
            return []
    except Exception as e:
        logging.error(f"Error fetching customers: {e}")
        return []

@st.cache_data(ttl=30)  # Cache for 30 seconds
def get_customer_info(customer_id):
    """Fetch customer information with caching"""
    try:
        response = requests.get(f"{API_BASE_URL}/customer/{customer_id}", timeout=3)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        logging.error(f"Error fetching customer info: {e}")
        return None

def send_message(message, customer_id, file=None):
    """Send message to chat API - optimized for speed"""
    try:
        if file:
            # Quick file size check (max 5MB for faster processing)
            if len(file.getvalue()) > 5 * 1024 * 1024:
                st.error("File too large. Please use images under 5MB for faster processing.")
                return None
            
            files = {'file': (file.name, file.getvalue(), 'image/jpeg')}
            data = {'message': message or "Refund request with image", 'customer_id': customer_id}
            response = requests.post(f"{API_BASE_URL}/validate", files=files, data=data, timeout=20)
        else:
            if not message or not message.strip():
                st.error("Please enter a message.")
                return None
            
            response = requests.post(f"{API_BASE_URL}/chat", 
                                   json={"message": message.strip(), "customer_id": customer_id}, 
                                   timeout=5)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Server error. Please try again.")
            return None
            
    except requests.exceptions.Timeout:
        st.error("Request timed out. Please try again.")
        return None
    except Exception as e:
        logging.error(f"Error: {e}")
        st.error("Please try again.")
        return None

@st.cache_data(ttl=10)  # Cache for 10 seconds - frequent updates needed
def get_escalations():
    """Get all escalated cases with caching"""
    try:
        response = requests.get(f"{API_BASE_URL}/escalations/all", timeout=3)
        if response.status_code == 200:
            return response.json().get('escalations', [])
        return []
    except Exception as e:
        logging.error(f"Error fetching escalations: {e}")
        return []

def resolve_escalation(case_id, resolution_type, notes):
    """Resolve an escalated case - optimized"""
    try:
        resolution_data = {
            "resolution_type": resolution_type,
            "notes": notes,
            "resolved_by": "Human Agent",
            "resolved_at": datetime.now().isoformat()
        }
        response = requests.post(f"{API_BASE_URL}/escalation/{case_id}/resolve", 
                               json=resolution_data, timeout=5)
        if response.status_code == 200:
            # Clear cache to show updated data
            get_escalations.clear()
            return True
        return False
    except Exception as e:
        logging.error(f"Error resolving case: {e}")
        return False

def customer_support_page():
    """Main customer support interface"""
    st.markdown("""
    <div class="main-header">
        <h1>🛒 CARE: Customer Assistance Resolution Engine</h1>
        <p>AI-powered customer support with intelligent resolution</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar for customer selection
    with st.sidebar:
        st.header("👤 Customer Selection")
        customers = get_customers()
        
        if customers:
            customer_options = {f"{c['name']} ({c['customer_id']})": c['customer_id'] for c in customers}
            selected_customer = st.selectbox(
                "Select Customer",
                options=list(customer_options.keys()),
                index=0 if customer_options else None,
                key="customer_selector"
            )
            customer_id = customer_options.get(selected_customer)
            
            if customer_id != st.session_state.selected_customer:
                st.session_state.selected_customer = customer_id
                st.session_state.messages = []
        else:
            st.warning("No customers available. Starting backend...")
            customer_id = None

        # Quick scenarios
        if customer_id:
            st.header("🚀 Quick Scenarios")
            scenarios = [
                "I want a refund for order ORD001",
                "Where is my order ORD002?",
                "My payment failed",
                "My wallet balance shows ₹0"
            ]
            for idx, scenario in enumerate(scenarios):
                if st.button(scenario, key=f"scenario_{idx}_{hash(scenario)}"):
                    response = send_message(scenario, customer_id)
                    if response:
                        st.session_state.messages.append({
                            "role": "user",
                            "content": scenario,
                            "timestamp": datetime.now().isoformat()
                        })
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response.get('response', 'Processing...'),
                            "intent": response.get('intent', 'None'),
                            "status": response.get('status', 'Processing'),
                            "timestamp": datetime.now().isoformat()
                        })
                        st.rerun()

    # Main content
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("💬 Chat Support")
        
        if not customer_id:
            st.info("Please select a customer to start chatting.")
        else:
            # Display chat history
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
                    if message["role"] == "assistant":
                        if message.get("intent"):
                            st.caption(f"Intent: {message['intent']} | Status: {message.get('status', 'N/A')}")

            # Chat input
            with st.form(key="chat_form", clear_on_submit=True):
                col_input, col_file = st.columns([3, 1])
                with col_input:
                    prompt = st.text_input("Message", placeholder="Enter your message...", key="chat_input")
                with col_file:
                    uploaded_file = st.file_uploader("Upload image", type=["jpg", "png"], label_visibility="collapsed", key="file_uploader")

                if st.form_submit_button("Send") and customer_id:
                    user_content = prompt or ("Image uploaded" if uploaded_file else "")
                    
                    if user_content or uploaded_file:
                        st.session_state.messages.append({
                            "role": "user",
                            "content": user_content,
                            "timestamp": datetime.now().isoformat()
                        })
                        
                        with st.spinner("Processing..."):
                            response = send_message(prompt, customer_id, uploaded_file)
                            
                        if response:
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": response.get('message', response.get('response', 'Processing...')),
                                "intent": response.get('intent', 'REFUND_REQUEST' if uploaded_file else 'Unknown'),
                                "status": response.get('status', 'Processing'),
                                "timestamp": datetime.now().isoformat()
                            })
                            
                            # Show status with detailed feedback
                            status = response.get('status')
                            if status == 'resolved':
                                st.success("✅ Request resolved successfully!")
                                if 'refund' in response.get('message', '').lower():
                                    st.balloons()  # Celebration for successful refund
                            elif status == 'escalated':
                                st.warning("⚠️ Request escalated for human review")
                                if response.get('case_id'):
                                    st.info(f"📋 Case ID: {response.get('case_id')} - You'll be notified once reviewed")
                            elif status == 'pending_image':
                                st.info("ℹ️ Please upload an image for validation")
                            elif status == 'error':
                                st.error("❌ There was an issue processing your request")
                            
                            # Show reference ID if available
                            if response.get('reference_id'):
                                st.info(f"🔖 Reference ID: {response.get('reference_id')}")
                        
                        st.rerun()

    with col2:
        # Customer info
        if customer_id:
            customer_info = get_customer_info(customer_id)
            if customer_info:
                customer = customer_info.get('customer', {})
                st.header("👤 Customer Info")
                st.markdown(f"""
                <div class="customer-info">
                    <strong>Name:</strong> {customer.get('name', 'N/A')}<br>
                    <strong>ID:</strong> {customer.get('customer_id', 'N/A')}<br>
                    <strong>Email:</strong> {customer.get('email', 'N/A')}<br>
                    <strong>Wallet:</strong> ₹{customer.get('wallet_balance', 0)}<br>
                    <strong>Membership:</strong> {customer.get('membership', 'N/A')}<br>
                    <strong>Location:</strong> {customer.get('location', 'N/A')}
                </div>
                """, unsafe_allow_html=True)

        # Quick stats
        st.header("📊 Quick Stats")
        try:
            response = requests.get(f"{API_BASE_URL}/analytics", timeout=5)
            if response.status_code == 200:
                analytics = response.json()
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Interactions", analytics.get('total_interactions', 0))
                with col2:
                    st.metric("Resolution Rate", f"{analytics.get('resolution_rate', 0)}%")
                with col3:
                    st.metric("Avg Response Time", f"{analytics.get('avg_response_time', 0)}s")
                
                # Show customer satisfaction if available
                if analytics.get('customer_satisfaction'):
                    st.metric("Customer Satisfaction", f"{analytics.get('customer_satisfaction', 0)}/5 ⭐")
            else:
                st.info("📊 Analytics will appear here once you start using the system")
        except Exception as e:
            logging.error(f"Analytics error: {e}")
            st.info("📊 Analytics temporarily unavailable")

def human_agent_page():
    """Human agent dashboard"""
    st.markdown("""
    <div class="main-header">
        <h1>👨‍💼 Human Agent Dashboard</h1>
        <p>Review and resolve escalated customer cases</p>
    </div>
    """, unsafe_allow_html=True)

    # Get escalations with error handling
    try:
        escalations = get_escalations()
    except Exception as e:
        st.error(f"Error loading escalations: {e}")
        escalations = []
    
    if not escalations:
        st.success("🎉 No escalated cases! All customers are happy.")
        return

    # Filter escalations
    pending_cases = [e for e in escalations if e.get('status') == 'pending']
    resolved_cases = [e for e in escalations if e.get('status') == 'resolved']

    # Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Pending Cases", len(pending_cases))
    with col2:
        st.metric("Resolved Cases", len(resolved_cases))
    with col3:
        st.metric("Total Cases", len(escalations))

    # Pending cases
    if pending_cases:
        st.subheader("🚨 Pending Cases")
        for idx, case in enumerate(pending_cases):
            case_id = case.get('case_id', f'Unknown_{idx}')
            customer_id = case.get('customer_id', 'Unknown')
            issue_details = case.get('issue_details', 'No details')
            
            # Create unique identifier for this case
            unique_id = f"{case_id}_{idx}"
            
            with st.expander(f"Case {case_id} - Customer {customer_id}"):
                st.text_area("Issue Details", value=issue_details, height=100, disabled=True, key=f"details_{unique_id}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"✅ Approve", key=f"approve_{unique_id}"):
                        if resolve_escalation(case_id, "approved", "Approved by human agent"):
                            st.success("Case approved!")
                            st.rerun()
                
                with col2:
                    if st.button(f"❌ Reject", key=f"reject_{unique_id}"):
                        if resolve_escalation(case_id, "rejected", "Rejected after review"):
                            st.success("Case rejected!")
                            st.rerun()
                
                with col3:
                    if st.button(f"📞 Contact", key=f"contact_{unique_id}"):
                        if resolve_escalation(case_id, "contact_required", "Customer contact needed"):
                            st.success("Marked for contact!")
                            st.rerun()

def main():
    """Main application entry point"""
    # Add professional header
    st.sidebar.markdown("---")
    st.sidebar.markdown("**🚀 Built with:**")
    st.sidebar.markdown("• LangGraph Agents")
    st.sidebar.markdown("• Multimodal AI (Gemini)")
    st.sidebar.markdown("• Human-in-the-Loop")
    st.sidebar.markdown("• MongoDB Atlas")
    st.sidebar.markdown("---")
    
    # Check environment variables first
    required_vars = ["GROQ_API_KEY", "GEMINI_API_KEY", "MONGODB_URI"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        st.error("❌ Configuration Required")
        st.info("Please set these environment variables in Streamlit Cloud settings:")
        for var in missing_vars:
            st.code(f"{var} = your_{var.lower()}_here")
        st.info("💡 Go to your app settings → Advanced settings → Secrets to add them.")
        return
    
    # Start backend with optimized UX
    if not st.session_state.backend_started:
        with st.spinner("🚀 Starting services..."):
            if not start_backend():
                st.error("❌ Failed to start services.")
                st.info("🔄 Please refresh the page.")
                return

    # Navigation
    st.sidebar.title("🛒 CARE System")
    page = st.sidebar.selectbox(
        "Navigate to:",
        ["Customer Support", "Human Agent Dashboard"],
        key="navigation_selector"
    )

    if page == "Customer Support":
        customer_support_page()
    elif page == "Human Agent Dashboard":
        human_agent_page()
    
    # Professional footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**💡 About CARE**")
    st.sidebar.markdown("AI-powered customer support with intelligent resolution and human oversight.")
    st.sidebar.markdown("**🔧 Features:**")
    st.sidebar.markdown("• Automated refund processing")
    st.sidebar.markdown("• Image damage analysis")
    st.sidebar.markdown("• Smart escalation system")
    st.sidebar.markdown("• Real-time analytics")

if __name__ == "__main__":
    main()