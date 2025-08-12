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
# Add src to path
sys.path.append('src')

# Page configuration
st.set_page_config(
    page_title="CARE: Customer Assistance Resolution Engine",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Environment setup
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:7860")

# Enhanced CSS for better UI
st.markdown("""
<style>
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container styling */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 50%, #2563eb 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(30, 58, 138, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* Customer info cards */
    .customer-info {
        background: linear-gradient(145deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #3b82f6;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    .customer-info:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
    }
    
    /* Metric containers */
    .metric-container {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
        border: 1px solid rgba(0,0,0,0.05);
        text-align: center;
    }
    
    .metric-container h4 {
        margin: 0 0 0.5rem 0;
        color: #64748b;
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-container h2 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    /* Chat interface styling */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.8);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
        background: linear-gradient(145deg, #3b82f6, #2563eb);
        color: white;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 16px rgba(59, 130, 246, 0.3);
        background: linear-gradient(145deg, #2563eb, #1d4ed8);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    /* Remove extra spacing */
    .stSelectbox {
        margin-bottom: 0.5rem !important;
    }
    
    /* Compact sidebar elements */
    .sidebar .element-container {
        margin-bottom: 0.5rem !important;
    }
    
    /* Remove default margins from markdown in sidebar */
    .sidebar .stMarkdown {
        margin-bottom: 0.5rem !important;
    }
    
    /* Compact customer info display */
    .customer-info {
        margin-top: 0.5rem !important;
        margin-bottom: 1rem !important;
    }
    
    /* Form styling */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        padding: 0.75rem;
        font-size: 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    /* Selectbox styling - Fixed visibility */
    .stSelectbox > div > div {
        background-color: #f8fafc !important;
        border-radius: 8px;
        border: 2px solid #cbd5e1 !important;
        color: #1f2937 !important;
    }
    
    /* Selectbox input field */
    .stSelectbox > div > div > div[data-baseweb="select"] > div {
        background-color: #f8fafc !important;
        color: #1f2937 !important;
        border: none !important;
    }
    
    /* Selectbox dropdown container */
    .stSelectbox [data-baseweb="popover"] {
        background-color: #ffffff !important;
        border: 2px solid #cbd5e1 !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.15) !important;
    }
    
    /* Selectbox dropdown options */
    .stSelectbox [role="option"] {
        background-color: #ffffff !important;
        color: #1f2937 !important;
        padding: 0.75rem 1rem !important;
        border-bottom: 1px solid #f1f5f9 !important;
    }
    
    /* Selectbox option hover state */
    .stSelectbox [role="option"]:hover {
        background-color: #3b82f6 !important;
        color: #ffffff !important;
    }
    
    /* Selectbox selected option */
    .stSelectbox [aria-selected="true"] {
        background-color: #1e40af !important;
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    /* Selectbox placeholder text */
    .stSelectbox [data-baseweb="select"] [data-baseweb="input"] {
        color: #1f2937 !important;
    }
    
    /* File uploader styling */
    .stFileUploader > div {
        border-radius: 8px;
        border: 2px dashed #cbd5e1;
        background: #f8fafc;
    }
    
    /* Success/Error message styling */
    .stSuccess {
        background: linear-gradient(145deg, #dcfce7, #bbf7d0);
        border-left: 5px solid #22c55e;
        border-radius: 8px;
    }
    
    .stError {
        background: linear-gradient(145deg, #fef2f2, #fecaca);
        border-left: 5px solid #ef4444;
        border-radius: 8px;
    }
    
    .stWarning {
        background: linear-gradient(145deg, #fffbeb, #fef3c7);
        border-left: 5px solid #f59e0b;
        border-radius: 8px;
    }
    
    .stInfo {
        background: linear-gradient(145deg, #eff6ff, #dbeafe);
        border-left: 5px solid #3b82f6;
        border-radius: 8px;
    }
    
    /* Quick action buttons */
    .quick-action-btn {
        width: 100%;
        margin-bottom: 0.5rem;
        padding: 0.75rem;
        background: linear-gradient(145deg, #f1f5f9, #e2e8f0);
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        color: #475569;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .quick-action-btn:hover {
        background: linear-gradient(145deg, #e2e8f0, #cbd5e1);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
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
        return False

@st.cache_data(ttl=30)
def get_subscriptions(customer_id):
    """Get customer subscriptions with caching"""
    try:
        response = requests.get(f"{API_BASE_URL}/subscriptions/{customer_id}", timeout=3)
        if response.status_code == 200:
            return response.json().get('subscriptions', [])
        return []
    except Exception as e:
        return []

def create_subscription(customer_id, items, delivery_date, subscription_type):
    """Create a new subscription"""
    try:
        subscription_data = {
            "customer_id": customer_id,
            "items": items,
            "delivery_date": delivery_date,
            "subscription_type": subscription_type
        }
        response = requests.post(f"{API_BASE_URL}/subscription", 
                               json=subscription_data, timeout=5)
        if response.status_code == 200:
            # Clear cache to show new subscription
            get_subscriptions.clear()
            return response.json()
        return None
    except Exception as e:
        return None

def cancel_subscription(subscription_id):
    """Cancel a subscription"""
    try:
        response = requests.post(f"{API_BASE_URL}/subscription/cancel/{subscription_id}", timeout=5)
        if response.status_code == 200:
            get_subscriptions.clear()
            return True
        return False
    except Exception as e:
        return False





def customer_support_page():
    """Main customer support interface"""
    
    # Customer selection
    customers = get_customers()
    if not customers:
        st.error("❌ No customers found. Please check backend connection.")
        st.info("💡 Make sure the backend service is running and accessible.")
        return
    
    # Sidebar with customer selection and quick actions
    with st.sidebar:
        st.markdown("### 👤 Select Customer")
        
        customer_options = [f"{c.get('name', 'Unknown')} ({c.get('customer_id', 'N/A')})" for c in customers]
        selected_idx = st.selectbox(
            "Choose a customer:",
            range(len(customer_options)),
            format_func=lambda x: customer_options[x],
            key="customer_selector",
            help="Select a customer to start providing support"
        )
        
        if selected_idx is not None:
            selected_customer = customers[selected_idx]
            st.session_state.selected_customer = selected_customer
            customer_id = selected_customer.get('customer_id')
            
            # Display customer info
            st.markdown(f"""
            <div class="customer-info">
                <strong>Name:</strong> {selected_customer.get('name', 'N/A')}<br>
                <strong>ID:</strong> {selected_customer.get('customer_id', 'N/A')}<br>
                <strong>Email:</strong> {selected_customer.get('email', 'N/A')}<br>
                <strong>Phone:</strong> {selected_customer.get('phone', 'N/A')}<br>
                <strong>Location:</strong> {selected_customer.get('location', 'N/A')}<br>
                <strong>Wallet:</strong> ₹{selected_customer.get('wallet_balance', 0)}<br>
                <strong>Membership:</strong> {selected_customer.get('membership', 'Regular')}
            </div>
            """, unsafe_allow_html=True)
            
            # Quick scenarios
            st.markdown("---")
            st.markdown("### 🚀 Quick Actions")
            st.markdown("*Click any scenario to start a conversation*")
            
            scenarios = [
                ("📦", "I want to check my recent orders"),
                ("💰", "I need help with a refund"),
                ("❌", "My payment failed"),
                ("💳", "Check my wallet balance"),
                ("🚚", "I want to track my delivery")
            ]
            
            for idx, (icon, scenario) in enumerate(scenarios):
                if st.button(f"{icon} {scenario}", key=f"scenario_{idx}_{hash(scenario)}", use_container_width=True):
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
        else:
            customer_id = None

    # Main content area
    if not customer_id:
        # Welcome screen when no customer is selected
        st.markdown("""
        <div style="text-align: center; padding: 3rem; background: linear-gradient(145deg, #f8fafc, #e2e8f0); border-radius: 15px; margin: 2rem 0;">
            <h2 style="color: #475569; margin-bottom: 1rem;">👋 Welcome to CARE Support</h2>
            <p style="color: #64748b; font-size: 1.1rem; margin-bottom: 2rem;">
                Select a customer from the sidebar to start providing AI-powered support
            </p>
            <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;">
                <div style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🤖</div>
                    <div style="font-weight: 600; color: #475569;">AI-Powered</div>
                    <div style="color: #64748b; font-size: 0.9rem;">Smart responses</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🖼️</div>
                    <div style="font-weight: 600; color: #475569;">Image Analysis</div>
                    <div style="color: #64748b; font-size: 0.9rem;">Visual validation</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">⚡</div>
                    <div style="font-weight: 600; color: #475569;">Fast Resolution</div>
                    <div style="color: #64748b; font-size: 0.9rem;">Quick solutions</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Chat interface when customer is selected
    col1, col2 = st.columns([2, 1], gap="large")

    with col1:
        st.markdown("### 💬 Chat Support")
        st.markdown("---")
        # Chat history container
        chat_container = st.container()
        with chat_container:
            if st.session_state.messages:
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.write(message["content"])
                        if message["role"] == "assistant":
                            if message.get("intent"):
                                st.caption(f"🎯 Intent: {message['intent']} | 📊 Status: {message.get('status', 'N/A')}")
            else:
                st.info("💬 Start a conversation by typing a message or using quick actions from the sidebar!")

        # Chat input form
        st.markdown("---")
        with st.form(key="chat_form", clear_on_submit=True):
            st.markdown("**💬 Send a message:**")
            col_input, col_file = st.columns([3, 1])
            
            with col_input:
                prompt = st.text_input(
                    "Message", 
                    placeholder="Type your message here...", 
                    key="chat_input",
                    label_visibility="collapsed"
                )
            
            with col_file:
                uploaded_file = st.file_uploader(
                    "📎 Upload image", 
                    type=["jpg", "jpeg", "png"], 
                    help="Upload an image for refund validation",
                    key="file_uploader"
                )

            col_send, col_clear = st.columns([1, 1])
            with col_send:
                send_clicked = st.form_submit_button("🚀 Send Message", use_container_width=True)
            with col_clear:
                if st.form_submit_button("🗑️ Clear Chat", use_container_width=True):
                    st.session_state.messages = []
                    st.rerun()

            if send_clicked and customer_id:
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
        # Customer details section
        if customer_id and st.session_state.selected_customer:
            customer = st.session_state.selected_customer
            st.markdown("### 👤 Customer Details")
            st.markdown("---")
            
            st.markdown(f"""
            <div class="customer-info">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <div style="font-size: 2rem; margin-right: 1rem;">👤</div>
                    <div>
                        <div style="font-weight: 700; font-size: 1.2rem; color: #1e40af;">{customer.get('name', 'N/A')}</div>
                        <div style="color: #64748b; font-size: 0.9rem;">ID: {customer.get('customer_id', 'N/A')}</div>
                    </div>
                </div>
                <div style="display: grid; gap: 0.5rem;">
                    <div><strong>📧 Email:</strong> {customer.get('email', 'N/A')}</div>
                    <div><strong>📱 Phone:</strong> {customer.get('phone', 'N/A')}</div>
                    <div><strong>📍 Location:</strong> {customer.get('location', 'N/A')}</div>
                    <div><strong>💳 Wallet:</strong> <span style="color: #059669; font-weight: 600;">₹{customer.get('wallet_balance', 0)}</span></div>
                    <div><strong>⭐ Membership:</strong> <span style="color: #7c3aed; font-weight: 600;">{customer.get('membership', 'Regular')}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # System Analytics section
        st.markdown("### 📊 System Analytics")
        st.markdown("---")
        
        try:
            response = requests.get(f"{API_BASE_URL}/analytics", timeout=5)
            if response.status_code == 200:
                analytics = response.json()
                
                # Main metrics
                st.markdown(f"""
                <div class="metric-container">
                    <h4>🔢 Total Interactions</h4>
                    <h2 style="color: #3b82f6;">{analytics.get('total_interactions', 0)}</h2>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="metric-container">
                    <h4>✅ Resolution Rate</h4>
                    <h2 style="color: #10b981;">{analytics.get('resolution_rate', 0)}%</h2>
                </div>
                """, unsafe_allow_html=True)
                
                # Additional metrics in smaller format
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("⚡ Response", f"{analytics.get('avg_response_time', 0)}s")
                with col_b:
                    if analytics.get('customer_satisfaction'):
                        st.metric("⭐ Rating", f"{analytics.get('customer_satisfaction', 0)}/5")
                    else:
                        st.metric("🎯 Status", "Active")
                        
            else:
                st.markdown("""
                <div class="metric-container">
                    <h4>📊 Analytics Dashboard</h4>
                    <p style="color: #64748b; margin: 0;">Start conversations to see metrics</p>
                </div>
                """, unsafe_allow_html=True)
                
        except Exception as e:
            st.markdown("""
            <div class="metric-container">
                <h4>📊 Analytics Loading...</h4>
                <p style="color: #64748b; margin: 0;">Please wait while we fetch the data</p>
            </div>
            """, unsafe_allow_html=True)

def subscription_page():
    """Subscription management page"""
    st.subheader("📦 Subscription Manager")
    
    # Customer selection in sidebar
    customers = get_customers()
    if not customers:
        st.error("No customers found. Please check backend connection.")
        return
    
    with st.sidebar:
        st.header("👤 Select Customer")
        customer_options = [f"{c.get('name', 'Unknown')} ({c.get('customer_id', 'N/A')})" for c in customers]
        selected_idx = st.selectbox(
            "Choose a customer:",
            range(len(customer_options)),
            format_func=lambda x: customer_options[x],
            key="subscription_customer_selector"
        )
        
        if selected_idx is not None:
            customer = customers[selected_idx]
            customer_id = customer.get('customer_id')
            
            # Display customer info
            st.markdown(f"""
            <div class="customer-info">
                <strong>Name:</strong> {customer.get('name', 'N/A')}<br>
                <strong>ID:</strong> {customer.get('customer_id', 'N/A')}<br>
                <strong>Email:</strong> {customer.get('email', 'N/A')}<br>
                <strong>Wallet:</strong> ₹{customer.get('wallet_balance', 0)}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Please select a customer to manage subscriptions.")
            return

    # Two columns layout
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📋 Active Subscriptions")
        subscriptions = get_subscriptions(customer_id)
        
        if subscriptions:
            for sub in subscriptions:
                if sub.get('status') == 'active':
                    with st.container():
                        st.markdown(f"""
                        <div class="customer-info">
                            <strong>🆔 ID:</strong> {sub.get('subscription_id', 'N/A')}<br>
                            <strong>📦 Items:</strong> {len(sub.get('items', []))} items<br>
                            <strong>📅 Delivery:</strong> {sub.get('delivery_date', 'N/A')}<br>
                            <strong>🔄 Type:</strong> {sub.get('subscription_type', 'weekly').title()}<br>
                            <strong>📊 Status:</strong> {sub.get('status', 'unknown').title()}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button(f"❌ Cancel {sub.get('subscription_id')}", 
                                   key=f"cancel_{sub.get('subscription_id')}"):
                            if cancel_subscription(sub.get('subscription_id')):
                                st.success("Subscription cancelled!")
                                st.rerun()
                            else:
                                st.error("Failed to cancel subscription")
        else:
            st.info("No active subscriptions found.")

    with col2:
        st.subheader("➕ Create New Subscription")
        
        with st.form("subscription_form"):
            # Available items
            available_items = [
                {"name": "Amul Milk 1L", "price": 60.0},
                {"name": "Fresh Vegetables Bundle", "price": 300.0},
                {"name": "Basmati Rice 5kg", "price": 450.0},
                {"name": "Fortune Oil 1L", "price": 180.0},
                {"name": "Tide Detergent 1kg", "price": 250.0},
                {"name": "Britannia Biscuits", "price": 150.0}
            ]
            
            selected_items = st.multiselect(
                "Select Items",
                options=[f"{item['name']} - ₹{item['price']}" for item in available_items],
                key="subscription_items"
            )
            
            delivery_date = st.date_input(
                "Next Delivery Date",
                value=datetime.now().date(),
                key="delivery_date"
            )
            
            subscription_type = st.selectbox(
                "Subscription Type",
                options=["weekly", "monthly"],
                key="subscription_type"
            )
            
            if st.form_submit_button("🚀 Create Subscription"):
                if selected_items:
                    # Parse selected items
                    items = []
                    for item_str in selected_items:
                        for item in available_items:
                            if item_str.startswith(item['name']):
                                items.append(item)
                                break
                    
                    result = create_subscription(
                        customer_id, 
                        items, 
                        delivery_date.isoformat(), 
                        subscription_type
                    )
                    
                    if result:
                        st.success(f"✅ Subscription created! ID: {result.get('subscription_id')}")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("Failed to create subscription")
                else:
                    st.error("Please select at least one item")

def human_agent_page():
    """Human agent dashboard"""
    st.subheader("👨‍💼 Human Agent Dashboard")

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

    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>🛒 CARE: Customer Assistance Resolution Engine</h1>
        <p>AI-powered customer support system with intelligent resolution capabilities</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem; background: linear-gradient(145deg, #1e40af, #3b82f6); border-radius: 10px; margin-bottom: 2rem;">
            <h2 style="color: white; margin: 0; font-size: 1.5rem;">🛒 CARE System</h2>
            <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0; font-size: 0.9rem;">AI Customer Support</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🧭 Navigation")
        page = st.selectbox(
            "Choose a section:",
            ["Customer Support", "Subscription Manager", "Human Agent Dashboard"],
            key="navigation_selector",
            help="Select the section you want to access"
        )

    if page == "Customer Support":
        customer_support_page()
    elif page == "Subscription Manager":
        subscription_page()
    elif page == "Human Agent Dashboard":
        human_agent_page()
    
    # Enhanced footer
    with st.sidebar:
        st.markdown("---")
        st.markdown("""
        <div style="background: linear-gradient(145deg, #f1f5f9, #e2e8f0); padding: 1rem; border-radius: 10px; text-align: center;">
            <div style="font-weight: 600; color: #475569; margin-bottom: 0.5rem;">✨ System Features</div>
            <div style="display: grid; gap: 0.3rem; font-size: 0.85rem; color: #64748b;">
                <div>🤖 Smart AI Processing</div>
                <div>🖼️ Image Analysis</div>
                <div>👥 Human Oversight</div>
                <div>📊 Real-time Analytics</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align: center; margin-top: 1rem; padding: 0.5rem; color: #94a3b8; font-size: 0.8rem;">
            <div>💡 CARE System v1.0</div>
            <div>AI-powered customer support</div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()