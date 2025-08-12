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

# Enhanced CSS for better UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #0078d4 0%, #005a9e 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,120,212,0.3);
    }
    .customer-info {
        background: linear-gradient(145deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 6px solid #0078d4;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        transition: transform 0.2s ease;
    }
    .customer-info:hover {
        transform: translateY(-2px);
    }
    .escalation-card {
        background: linear-gradient(145deg, #fff3cd 0%, #ffeaa7 100%);
        padding: 1rem;
        border-radius: 12px;
        border-left: 4px solid #ffc107;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(255,193,7,0.2);
    }
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .stSelectbox > div > div {
        background-color: white;
        border-radius: 8px;
    }
    .stButton > button {
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_info" not in st.session_state:
    st.session_state.user_info = None
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

@st.cache_data(ttl=30)
def get_subscriptions(customer_id):
    """Get customer subscriptions with caching"""
    try:
        response = requests.get(f"{API_BASE_URL}/subscriptions/{customer_id}", timeout=3)
        if response.status_code == 200:
            return response.json().get('subscriptions', [])
        return []
    except Exception as e:
        logging.error(f"Error fetching subscriptions: {e}")
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
        logging.error(f"Error creating subscription: {e}")
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
        logging.error(f"Error cancelling subscription: {e}")
        return False

def register_user(name, email, phone, location):
    """Register a new user"""
    try:
        user_data = {
            "name": name.strip(),
            "email": email.strip(),
            "phone": phone.strip(),
            "location": location.strip(),
            "join_date": datetime.now().isoformat()
        }
        response = requests.post(f"{API_BASE_URL}/register", json=user_data, timeout=5)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            error_detail = response.json().get("detail", "Registration failed")
            st.error(f"❌ {error_detail}")
            return None
        else:
            st.error("❌ Registration failed. Please try again.")
            return None
    except Exception as e:
        logging.error(f"Error registering user: {e}")
        st.error("❌ Connection error. Please try again.")
        return None

def login_user(email, phone):
    """Login user with email and phone"""
    try:
        login_data = {"email": email.strip(), "phone": phone.strip()}
        response = requests.post(f"{API_BASE_URL}/login", json=login_data, timeout=5)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            error_detail = response.json().get("detail", "Invalid credentials")
            st.error(f"❌ {error_detail}")
            return None
        else:
            st.error("❌ Login failed. Please try again.")
            return None
    except Exception as e:
        logging.error(f"Error logging in: {e}")
        st.error("❌ Connection error. Please try again.")
        return None

def login_page():
    """User authentication page"""
    st.markdown("""
    <div class="main-header">
        <h1>🛒 Welcome to CARE</h1>
        <p>Customer Assistance Resolution Engine</p>
    </div>
    """, unsafe_allow_html=True)

    # Login/Register tabs
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])
    
    with tab1:
        st.subheader("Login to Your Account")
        with st.form("login_form"):
            email = st.text_input("📧 Email Address", placeholder="priya.sharma@gmail.com")
            
            col1, col2 = st.columns([1, 3])
            with col1:
                country_code = st.selectbox("🌍", ["+91", "+1", "+44", "+86"], index=0, key="login_country")
            with col2:
                phone_number = st.text_input("📱 Phone Number", placeholder="9876543210", label_visibility="collapsed")
            
            if st.form_submit_button("🚀 Login", use_container_width=True):
                if email and phone_number:
                    full_phone = f"{country_code}-{phone_number}"
                    with st.spinner("Logging in..."):
                        user_data = login_user(email, full_phone)
                        if user_data:
                            st.session_state.logged_in = True
                            st.session_state.user_info = user_data
                            st.success(f"Welcome back, {user_data.get('name', 'User')}!")
                            st.rerun()
                        # Error message is handled in login_user function
                else:
                    st.error("Please fill in all fields")
        

    
    with tab2:
        st.subheader("Create New Account")
        with st.form("register_form"):
            name = st.text_input("👤 Full Name", placeholder="John Doe")
            email = st.text_input("📧 Email Address", placeholder="john.doe@example.com")
            
            col1, col2 = st.columns([1, 3])
            with col1:
                country_code_reg = st.selectbox("🌍", ["+91", "+1", "+44", "+86"], index=0, key="register_country")
            with col2:
                phone_number_reg = st.text_input("📱 Phone Number", placeholder="9876543210", label_visibility="collapsed")
            
            location = st.text_input("📍 Location", placeholder="Mumbai, Maharashtra")
            
            if st.form_submit_button("✨ Create Account", use_container_width=True):
                if name and email and phone_number_reg and location:
                    full_phone = f"{country_code_reg}-{phone_number_reg}"
                    with st.spinner("Creating account..."):
                        user_data = register_user(name, email, full_phone, location)
                        if user_data:
                            st.session_state.logged_in = True
                            st.session_state.user_info = user_data
                            st.success(f"🎉 Welcome to CARE, {name}!")
                            st.balloons()
                            st.rerun()
                        # Error message is handled in register_user function
                else:
                    st.error("Please fill in all fields")

    # Debug section
    st.markdown("---")
    with st.expander("🔧 Debug Info"):
        if st.button("Test Backend Connection"):
            try:
                response = requests.get(f"{API_BASE_URL}/health", timeout=5)
                if response.status_code == 200:
                    health_data = response.json()
                    st.success(f"✅ Backend connected! Database: {health_data.get('database')}, Customers: {health_data.get('customers_count')}")
                else:
                    st.error(f"❌ Backend error: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Connection failed: {e}")
        
        if st.button("Show Available Users"):
            try:
                response = requests.get(f"{API_BASE_URL}/customers", timeout=5)
                if response.status_code == 200:
                    customers = response.json().get('customers', [])
                    st.write("Available users for testing:")
                    for c in customers[:3]:  # Show first 3
                        st.write(f"📧 {c.get('email')} | 📱 {c.get('phone')}")
                else:
                    st.error("Failed to fetch customers")
            except Exception as e:
                st.error(f"Error: {e}")

def customer_support_page():
    """Main customer support interface"""
    user = st.session_state.user_info
    
    st.markdown(f"""
    <div class="main-header">
        <h1>🛒 Welcome, {user.get('name', 'User')}!</h1>
        <p>How can we help you today?</p>
    </div>
    """, unsafe_allow_html=True)

    customer_id = user.get('customer_id')
    
    # Sidebar with user info and quick actions
    with st.sidebar:
        st.header("👤 Your Account")
        st.markdown(f"""
        <div class="customer-info">
            <strong>Name:</strong> {user.get('name', 'N/A')}<br>
            <strong>Email:</strong> {user.get('email', 'N/A')}<br>
            <strong>Phone:</strong> {user.get('phone', 'N/A')}<br>
            <strong>Location:</strong> {user.get('location', 'N/A')}<br>
            <strong>Wallet:</strong> ₹{user.get('wallet_balance', 0)}<br>
            <strong>Membership:</strong> {user.get('membership', 'Regular')}
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_info = None
            st.session_state.messages = []
            st.rerun()

        # Quick scenarios
        st.header("🚀 Quick Actions")
        scenarios = [
            "I want to check my recent orders",
            "I need help with a refund",
            "My payment failed",
            "Check my wallet balance",
            "I want to track my delivery"
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

        # Enhanced stats display
        st.header("📊 System Analytics")
        try:
            response = requests.get(f"{API_BASE_URL}/analytics", timeout=5)
            if response.status_code == 200:
                analytics = response.json()
                
                # Main metrics in cards
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("""
                    <div class="metric-container">
                        <h4>🔢 Total Interactions</h4>
                        <h2 style="color: #0078d4;">{}</h2>
                    </div>
                    """.format(analytics.get('total_interactions', 0)), unsafe_allow_html=True)
                    
                with col2:
                    st.markdown("""
                    <div class="metric-container">
                        <h4>✅ Resolution Rate</h4>
                        <h2 style="color: #22c55e;">{}%</h2>
                    </div>
                    """.format(analytics.get('resolution_rate', 0)), unsafe_allow_html=True)
                
                # Additional metrics
                col3, col4 = st.columns(2)
                with col3:
                    st.metric("⚡ Avg Response", f"{analytics.get('avg_response_time', 0)}s")
                with col4:
                    if analytics.get('customer_satisfaction'):
                        st.metric("⭐ Satisfaction", f"{analytics.get('customer_satisfaction', 0)}/5")
                    else:
                        st.metric("🎯 System Status", "Active")
                        
            else:
                st.markdown("""
                <div class="metric-container">
                    <h4>📊 Analytics Dashboard</h4>
                    <p>Start using the system to see analytics here</p>
                </div>
                """, unsafe_allow_html=True)
        except Exception as e:
            logging.error(f"Analytics error: {e}")
            st.info("📊 Analytics loading...")

def subscription_page():
    """Subscription management page"""
    user = st.session_state.user_info
    customer_id = user.get('customer_id')
    
    st.markdown(f"""
    <div class="main-header">
        <h1>📦 Your Subscriptions</h1>
        <p>Manage your recurring deliveries, {user.get('name', 'User')}</p>
    </div>
    """, unsafe_allow_html=True)

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

    # Check if user is logged in
    if not st.session_state.logged_in:
        login_page()
        return

    # Navigation for logged-in users
    st.sidebar.title("🛒 CARE System")
    page = st.sidebar.selectbox(
        "Navigate to:",
        ["Customer Support", "Subscription Manager", "Human Agent Dashboard"],
        key="navigation_selector"
    )

    if page == "Customer Support":
        customer_support_page()
    elif page == "Subscription Manager":
        subscription_page()
    elif page == "Human Agent Dashboard":
        human_agent_page()
    
    # Clean footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**💡 CARE System**")
    st.sidebar.markdown("*AI-powered customer support*")
    st.sidebar.markdown("---")
    st.sidebar.markdown("🤖 **Smart AI Processing**")
    st.sidebar.markdown("🖼️ **Image Analysis**") 
    st.sidebar.markdown("👥 **Human Oversight**")
    st.sidebar.markdown("📊 **Real-time Analytics**")

if __name__ == "__main__":
    main()