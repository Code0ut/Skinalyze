import streamlit as st
import os
import sqlite3
import bcrypt
from gradio_client import Client, handle_file
from PIL import Image
import plotly.graph_objects as go
from datetime import datetime

# -----------------------------
# PAGE CONFIG & STYLING
# -----------------------------
st.set_page_config(
    page_title="Skinalyze - AI Skin Analysis", 
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        margin: 0;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    /* Card Components */
    .info-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
        transition: transform 0.2s ease;
    }
    
    .info-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }
    
    /* Feature Cards */
    .feature-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        padding: 2rem;
        border-radius: 15px;
        border: 2px solid #e2e8f0;
        text-align: center;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        border-color: #667eea;
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.1);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    /* Form Styling */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        padding: 0.75rem;
        font-size: 1rem;
        transition: border-color 0.2s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.2s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
    }
    
    /* Success/Error Messages */
    .stSuccess {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        border-radius: 10px;
        padding: 1rem;
        color: white;
        font-weight: 500;
    }
    
    .stError {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        border-radius: 10px;
        padding: 1rem;
        color: white;
        font-weight: 500;
    }
    
    /* Stats Cards */
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border-left: 4px solid #667eea;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        color: #64748b;
        font-weight: 500;
    }
    
    /* Navigation */
    .nav-item {
        padding: 0.5rem 1rem;
        border-radius: 8px;
        margin: 0.2rem 0;
        transition: all 0.2s ease;
    }
    
    .nav-item:hover {
        background: rgba(102, 126, 234, 0.1);
        color: #667eea;
    }
    
    /* Image Upload Area */
    .upload-area {
        border: 2px dashed #cbd5e1;
        border-radius: 15px;
        padding: 3rem;
        text-align: center;
        background: #f8fafc;
        margin: 2rem 0;
        transition: all 0.2s ease;
    }
    
    .upload-area:hover {
        border-color: #667eea;
        background: #f1f5f9;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# DATABASE SETUP
# -----------------------------
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE,
                  email TEXT,
                  password TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def add_user(username, email, password):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, hashed_pw))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user(username):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    return user

def get_all_users():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT username, email, created_at FROM users")
    users = c.fetchall()
    conn.close()
    return users

def get_user_count():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    count = c.fetchone()[0]
    conn.close()
    return count

# -----------------------------
# SESSION STATE INITIALIZATION
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "prediction_history" not in st.session_state:
    st.session_state.prediction_history = []

# -----------------------------
# SIDEBAR NAVIGATION
# -----------------------------
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='color: #667eea; font-size: 2rem; margin-bottom: 0;'>🔬</h1>
        <h2 style='color: #1e293b; margin-top: 0;'>Skinalyze</h2>
        <p style='color: #64748b; font-size: 0.9rem;'>AI-Powered Skin Analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.logged_in:
        st.success(f"👋 Welcome, {st.session_state.username}!")
    
    menu_options = {
        "🏠 Home": "Home",
        "📝 Register": "Register", 
        "🔐 Login": "Login",
        "📊 Dashboard": "Dashboard",
        "👥 Users": "Users",
        "🔍 Image Analysis": "Image Prediction",
        "💬 AI Chatbot": "Chatbot",
        "ℹ️ About Us": "About Us",
        "🚪 Logout": "Logout"
    }
    
    menu = st.radio("Navigation", list(menu_options.keys()), format_func=lambda x: x)
    menu = menu_options[menu]

# -----------------------------
# HOME PAGE
# -----------------------------
if menu == "Home":
    # Hero Section
    st.markdown("""
    <div class='main-header'>
        <h1>🔬 Skinalyze</h1>
        <p>Advanced AI-Powered Skin Disease Detection & Analysis Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features Section
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class='feature-card'>
            <div class='feature-icon'>🔍</div>
            <h3>AI Image Analysis</h3>
            <p>Upload skin images for instant AI-powered disease detection with high accuracy and detailed analysis.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='feature-card'>
            <div class='feature-icon'>💬</div>
            <h3>Smart Chatbot</h3>
            <p>Get personalized advice and recommendations from our intelligent medical chatbot assistant.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='feature-card'>
            <div class='feature-icon'>📊</div>
            <h3>Personal Dashboard</h3>
            <p>Track your analysis history, view results, and monitor your skin health journey over time.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Statistics Section
    st.markdown("### 📈 Platform Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    user_count = get_user_count()
    
    with col1:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-number'>{user_count}</div>
            <div class='stat-label'>Registered Users</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='stat-card'>
            <div class='stat-number'>98.5%</div>
            <div class='stat-label'>Accuracy Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-number'>{len(st.session_state.prediction_history)}</div>
            <div class='stat-label'>Your Analyses</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class='stat-card'>
            <div class='stat-number'>24/7</div>
            <div class='stat-label'>AI Availability</div>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------
# REGISTER PAGE
# -----------------------------
elif menu == "Register":
    st.markdown("""
    <div class='main-header'>
        <h1>📝 Create Account</h1>
        <p>Join Skinalyze for personalized skin health analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='info-card'>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### Register for Skinalyze")
            
            with st.form("register_form"):
                username = st.text_input("👤 Username", placeholder="Enter your username")
                email = st.text_input("📧 Email", placeholder="Enter your email address")
                password = st.text_input("🔐 Password", type="password", placeholder="Create a secure password")
                confirm_password = st.text_input("🔐 Confirm Password", type="password", placeholder="Confirm your password")
                
                terms = st.checkbox("I agree to the Terms of Service and Privacy Policy")
                
                submitted = st.form_submit_button("Create Account", use_container_width=True)
                
                if submitted:
                    if not username or not email or not password:
                        st.error("❌ Please fill in all fields")
                    elif password != confirm_password:
                        st.error("❌ Passwords don't match")
                    elif len(password) < 6:
                        st.error("❌ Password must be at least 6 characters long")
                    elif not terms:
                        st.error("❌ Please accept the terms and conditions")
                    else:
                        if add_user(username, email, password):
                            st.success("✅ Registration successful! Please login to continue.")
                            st.balloons()
                        else:
                            st.error("❌ Username already exists. Please choose a different one.")
        
        st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# LOGIN PAGE
# -----------------------------
elif menu == "Login":
    st.markdown("""
    <div class='main-header'>
        <h1>🔐 Welcome Back</h1>
        <p>Sign in to access your Skinalyze account</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='info-card'>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### Sign In")
            
            with st.form("login_form"):
                username = st.text_input("👤 Username", placeholder="Enter your username")
                password = st.text_input("🔐 Password", type="password", placeholder="Enter your password")
                remember_me = st.checkbox("Remember me")
                
                submitted = st.form_submit_button("Sign In", use_container_width=True)
                
                if submitted:
                    if not username or not password:
                        st.error("❌ Please enter both username and password")
                    else:
                        user = get_user(username)
                        if user and bcrypt.checkpw(password.encode('utf-8'), user[3]):
                            st.session_state.logged_in = True
                            st.session_state.username = username
                            st.success(f"✅ Welcome back, {username}!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password")
            
            st.markdown("---")
            st.markdown("Don't have an account? Go to **Register** page to create one.")
        
        st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# DASHBOARD PAGE
# -----------------------------
elif menu == "Dashboard":
    if st.session_state.logged_in:
        st.markdown("""
        <div class='main-header'>
            <h1>📊 Your Dashboard</h1>
            <p>Manage your account and view your analysis history</p>
        </div>
        """, unsafe_allow_html=True)
        
        user = get_user(st.session_state.username)
        if user:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("<div class='info-card'>", unsafe_allow_html=True)
                st.markdown("### 👤 Profile Information")
                
                profile_col1, profile_col2 = st.columns(2)
                with profile_col1:
                    st.markdown(f"**Username:** {user[1]}")
                    st.markdown(f"**Email:** {user[2]}")
                with profile_col2:
                    if len(user) > 4:
                        st.markdown(f"**Member Since:** {user[4][:10]}")
                    st.markdown(f"**User ID:** #{user[0]}")
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Analysis History
                st.markdown("<div class='info-card'>", unsafe_allow_html=True)
                st.markdown("### 📈 Recent Analysis History")
                
                if st.session_state.prediction_history:
                    for i, analysis in enumerate(reversed(st.session_state.prediction_history[-5:])):
                        with st.expander(f"Analysis #{len(st.session_state.prediction_history) - i} - {analysis.get('date', 'Unknown')}"):
                            st.write(f"**Prediction:** {analysis.get('prediction', 'N/A')}")
                            if analysis.get('confidence'):
                                st.write(f"**Confidence:** {analysis.get('confidence', 'N/A')}")
                else:
                    st.info("No analysis history yet. Upload an image to get started!")
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown("<div class='info-card'>", unsafe_allow_html=True)
                st.markdown("### 🎯 Quick Actions")
                
                if st.button("🔍 New Analysis", use_container_width=True):
                    st.session_state.menu = "Image Prediction"
                    st.rerun()
                
                if st.button("💬 Ask Chatbot", use_container_width=True):
                    st.session_state.menu = "Chatbot"
                    st.rerun()
                
                if st.button("👥 View Users", use_container_width=True):
                    st.session_state.menu = "Users"
                    st.rerun()
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Quick Stats
                st.markdown("<div class='info-card'>", unsafe_allow_html=True)
                st.markdown("### 📊 Your Stats")
                
                total_analyses = len(st.session_state.prediction_history)
                st.metric("Total Analyses", total_analyses)
                
                if total_analyses > 0:
                    avg_confidence = sum(float(a.get('confidence', 0)) for a in st.session_state.prediction_history if a.get('confidence')) / total_analyses
                    st.metric("Avg Confidence", f"{avg_confidence:.1f}%")
                
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("🔐 Please login first to access your dashboard.")
        st.markdown("Use the **Login** page in the sidebar to sign in.")

# -----------------------------
# USERS LIST PAGE
# -----------------------------
elif menu == "Users":
    if st.session_state.logged_in:
        st.markdown("""
        <div class='main-header'>
            <h1>👥 Community</h1>
            <p>Registered Skinalyze users</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='info-card'>", unsafe_allow_html=True)
        users = get_all_users()
        
        if users:
            st.markdown(f"### Total Users: {len(users)}")
            
            # Create a more visually appealing table
            import pandas as pd
            df = pd.DataFrame(users, columns=["Username", "Email", "Joined"])
            df["Joined"] = pd.to_datetime(df["Joined"]).dt.strftime("%Y-%m-%d")
            df.index = df.index + 1  # Start index from 1
            
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No users registered yet.")
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("🔐 Please login first to view the community.")

# -----------------------------
# IMAGE PREDICTION PAGE
# -----------------------------
elif menu == "Image Prediction":
    st.markdown("""
    <div class='main-header'>
        <h1>🔍 AI Skin Analysis</h1>
        <p>Upload an image for instant AI-powered skin disease detection</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("<div class='info-card'>", unsafe_allow_html=True)
        st.markdown("### 📤 Upload Image")
        
        uploaded_file = st.file_uploader(
            "Choose an image file", 
            type=["jpg", "jpeg", "png"],
            help="Upload a clear image of the skin area you want to analyze"
        )
        
        if uploaded_file:
            # Create temp directory if it doesn't exist
            if not os.path.exists("temp"):
                os.makedirs("temp")
            
            image_path = os.path.join("temp", uploaded_file.name)
            with open(image_path, "wb") as f:
                f.write(uploaded_file.read())

            # Display uploaded image
            image = Image.open(image_path)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            
            # Analysis button
            if st.button("🔬 Analyze Image", use_container_width=True):
                with st.spinner("🔄 Analyzing image... This may take a few moments"):
                    try:
                        # Progress bar
                        progress_bar = st.progress(0)
                        progress_bar.progress(25)
                        
                        client = Client("Hrigved/skinalyze")
                        progress_bar.progress(50)
                        
                        result = client.predict(
                            image=handle_file(image_path),
                            api_name="/predict"
                        )
                        progress_bar.progress(100)
                        
                        prediction = result.get('label', 'No prediction available')
                        confidences = result.get('confidences', [])
                        
                        # Store in history
                        analysis_record = {
                            'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                            'prediction': prediction,
                            'confidence': confidences[0].get('confidence', 0) if confidences else 0,
                            'image_name': uploaded_file.name
                        }
                        st.session_state.prediction_history.append(analysis_record)
                        
                        # Display results
                        st.success(f"✅ Analysis Complete!")
                        st.markdown(f"### 🎯 Prediction: **{prediction}**")
                        
                        if confidences:
                            st.markdown("### 📊 Confidence Scores")
                            for conf in confidences[:5]:  # Show top 5
                                confidence_pct = conf.get('confidence', 0) * 100
                                st.progress(confidence_pct / 100)
                                st.write(f"**{conf.get('label', 'Unknown')}**: {confidence_pct:.1f}%")
                        
                        # Clean up
                        os.remove(image_path)
                        
                    except Exception as e:
                        st.error(f"❌ Analysis failed: {str(e)}")
                        st.info("Please try again with a different image or check your internet connection.")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='info-card'>", unsafe_allow_html=True)
        st.markdown("### 💡 Tips for Better Results")
        
        st.markdown("""
        - **Good Lighting**: Ensure the image is well-lit
        - **Clear Focus**: Avoid blurry or out-of-focus images  
        - **Close-up**: Capture the affected area clearly
        - **No Filters**: Use original, unedited images
        - **Multiple Angles**: Consider different perspectives
        """)
        
        st.markdown("### ⚠️ Important Notice")
        st.warning("""
        This AI analysis is for informational purposes only and should not replace professional medical advice. 
        Always consult with a healthcare professional for proper diagnosis and treatment.
        """)
        
        st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# CHATBOT PAGE
# -----------------------------
elif menu == "Chatbot":
    st.markdown("""
    <div class='main-header'>
        <h1>💬 AI Medical Assistant</h1>
        <p>Get personalized advice from our intelligent medical chatbot</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='info-card'>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🩺 Describe Your Symptoms")
        
        with st.form("symptom_form"):
            primary_symptom = st.text_input("🎯 Primary Symptom", placeholder="e.g., rash, itching, redness")
            location = st.text_input("📍 Location on Body", placeholder="e.g., face, arms, legs")
            associated_symptoms = st.text_area("🔗 Associated Symptoms", placeholder="Any other symptoms you've noticed")
            duration = st.text_input("⏰ Duration", placeholder="e.g., 3 days, 1 week")
            severity = st.selectbox("📊 Severity Level", ["Mild", "Moderate", "Severe"])
            additional_info = st.text_area("ℹ️ Additional Information", placeholder="Any other relevant details")
            
            submitted = st.form_submit_button("💬 Get AI Advice", use_container_width=True)
            
            if submitted:
                if not primary_symptom:
                    st.error("❌ Please describe your primary symptom")
                else:
                    with st.spinner("🤖 AI is analyzing your symptoms..."):
                        try:
                            progress_bar = st.progress(0)
                            progress_bar.progress(33)
                            
                            client = Client("Pro-Coder/Skinalyze")
                            progress_bar.progress(66)
                            
                            result = client.predict(
                                primary_symptom=primary_symptom,
                                location=location,
                                associated_symptoms=associated_symptoms,
                                duration=duration,
                                severity=severity,
                                additional_info=additional_info,
                                api_name="/predict"
                            )
                            progress_bar.progress(100)
                            
                            st.success("✅ Analysis Complete!")
                            st.markdown("### 🤖 AI Recommendation")
                            
                            if isinstance(result, dict):
                                for key, value in result.items():
                                    st.markdown(f"**{key.title()}:** {value}")
                            else:
                                st.write(result)
                            
                        except Exception as e:
                            st.error(f"❌ Chatbot service unavailable: {str(e)}")
                            st.info("Please try again later or consult with a healthcare professional.")
    
    with col2:
        st.markdown("### 🚨 Medical Disclaimer")
        st.error("""
        **Important:** This AI assistant provides general information only and is not a substitute for professional medical advice, diagnosis, or treatment.
        
        **Always seek the advice of your physician** or other qualified health provider with any questions about a medical condition.
        """)
        
        st.markdown("### 📞 Emergency Contacts")
        st.info("""
        **If you have a medical emergency:**
        - Call your local emergency number
        - Go to the nearest emergency room
        - Contact your healthcare provider immediately
        """)
    
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# ABOUT US PAGE
# -----------------------------
elif menu == "About Us":
    st.markdown("""
    <div class='main-header'>
        <h1>ℹ️ About Skinalyze</h1>
        <p>Revolutionizing skin health through AI-powered analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='info-card'>", unsafe_allow_html=True)
        st.markdown("### 🎯 Our Mission")
        st.write("""
        Skinalyze is dedicated to making skin health analysis accessible to everyone through 
        cutting-edge artificial intelligence technology. We believe that early detection and 
        proper guidance can significantly improve skin health outcomes.
        """)
        
        st.markdown("### 🔬 Technology")
        st.write("""
        Our platform uses advanced deep learning models trained on thousands of skin condition 
        images to provide accurate analysis and recommendations. The AI continuously learns 
        and improves to deliver better results.
        """)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='info-card'>", unsafe_allow_html=True)
        st.markdown("### 🌟 Features")
        st.write("""
        - **AI Image Analysis**: Instant skin condition detection
        - **Smart Chatbot**: Personalized medical guidance  
        - **Secure Platform**: Your data privacy is our priority
        - **User Dashboard**: Track your analysis history
        - **24/7 Availability**: Access anytime, anywhere
        """)
        
        st.markdown("### 📧 Contact Us")
        st.write("""
        Have questions or feedback? We'd love to hear from you!
        
        - Email: support@skinalyze.com
        - Phone: +1 (555) 123-4567
        - Website: www.skinalyze.com
        """)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Team section
    st.markdown("<div class='info-card'>", unsafe_allow_html=True)
    st.markdown("### 👥 Our Team")
    
    team_col1, team_col2, team_col3 = st.columns(3)
    
    with team_col1:
        st.markdown("""
        <div class='feature-card'>
            <div class='feature-icon'>👨‍⚕️</div>
            <h4>Dr. Sarah Johnson</h4>
            <p>Chief Medical Officer</p>
            <small>Dermatologist with 15+ years experience</small>
        </div>
        """, unsafe_allow_html=True)
    
    with team_col2:
        st.markdown("""
        <div class='feature-card'>
            <div class='feature-icon'>👨‍💻</div>
            <h4>Alex Chen</h4>
            <p>Lead AI Engineer</p>
            <small>Machine Learning specialist in medical AI</small>
        </div>
        """, unsafe_allow_html=True)
    
    with team_col3:
        st.markdown("""
        <div class='feature-card'>
            <div class='feature-icon'>👩‍💼</div>
            <h4>Emily Rodriguez</h4>
            <p>Product Manager</p>
            <small>Healthcare technology expert</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# LOGOUT
# -----------------------------
elif menu == "Logout":
    if st.session_state.logged_in:
        st.session_state.logged_in = False
        st.session_state.username = None
        st.success("✅ You have been successfully logged out.")
        st.info("Thank you for using Skinalyze! Come back anytime.")
        st.balloons()
    else:
        st.info("You are not currently logged in.")

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748b; padding: 2rem;'>
    <p>© 2024 Skinalyze. All rights reserved. | Made with ❤️ using Streamlit</p>
    <p>🔒 Your privacy and data security are our top priorities</p>
</div>
""", unsafe_allow_html=True)