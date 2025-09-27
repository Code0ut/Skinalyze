import streamlit as st
import os
import sqlite3
import bcrypt
from gradio_client import Client, handle_file
from PIL import Image
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
import joblib
import time

# -----------------------------
# PAGE CONFIG & STYLING
# -----------------------------
st.set_page_config(
    page_title="Arogya Sahayak & Skinalyze - Complete Health Assistant", 
    page_icon="🩺",
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
# TRANSLATION DICTIONARY
# -----------------------------
translations = {
    "app_title": {
        "en": "Arogya Sahayak & Skinalyze | Complete Health Assistant",
        "mr": "आरोग्य सहायक आणि स्किनलायझ | संपूर्ण आरोग्य सहायक",
        "hi": "आरोग्य सहायक और स्किनलायझ | संपूर्ण स्वास्थ्य सहायक"
    },
    "language_label": {"en": "Select Language", "mr": "भाषा निवडा", "hi": "भाषा चुनें"},
    "maternal_tool_name": {"en": "Maternal Health Risk", "mr": "माता आरोग्य जोखीम", "hi": "मातृ स्वास्थ्य जोखिम"},
    "disease_tool_name": {"en": "Disease Prediction", "mr": "रोग निदान", "hi": "रोग निदान"},
    "skin_analysis_name": {"en": "Skin Analysis", "mr": "त्वचा विश्लेषण", "hi": "त्वचा विश्लेषण"},
    "chatbot_name": {"en": "Medical Chatbot", "mr": "वैद्यकीय चॅटबॉट", "hi": "चिकित्सा चैटबॉट"},
    "home_name": {"en": "Home", "mr": "मुख्यपृष्ठ", "hi": "होम"},
    "register_name": {"en": "Register", "mr": "नोंदणी", "hi": "रजिस्टर"},
    "login_name": {"en": "Login", "mr": "लॉगिन", "hi": "लॉगिन"},
    "dashboard_name": {"en": "Dashboard", "mr": "डॅशबोर्ड", "hi": "डैशबोर्ड"},
    "users_name": {"en": "Users", "mr": "वापरकर्ते", "hi": "उपयोगकर्ता"},
    "about_name": {"en": "About Us", "mr": "आमच्याबद्दल", "hi": "हमारे बारे में"},
    "logout_name": {"en": "Logout", "mr": "लॉगआउट", "hi": "लॉगआउट"},
    
    # Maternal Health
    "maternal_title": {"en": "👩‍⚕️ Maternal Health Risk Predictor", "mr": "👩‍⚕️ माता आरोग्य जोखीम निदान", "hi": "👩‍⚕️ मातृ स्वास्थ्य जोखिम भविष्यवक्ता"},
    "maternal_desc": {
        "en": "Enter patient vitals to assess maternal health risk. Ideal for routine checks by health workers.",
        "mr": "आरोग्य कर्मचाऱ्यांद्वारे नियमित तपासणीसाठी, माता आरोग्य जोखीम मूल्यांकन करण्यासाठी रुग्णाचे तपशील प्रविष्ट करा.",
        "hi": "मातृ स्वास्थ्य जोखिम का आकलन करने के लिए रोगी के महत्वपूर्ण आँकड़े दर्ज करें। स्वास्थ्य कर्मियों द्वारा नियमित जांच के लिए आदर्श।"
    },
    "vitals_header": {"en": "Enter Patient Vitals", "mr": "रुग्णाचे तपशील प्रविष्ट करा", "hi": "रोगी के महत्वपूर्ण आँकड़े दर्ज करें"},
    "age": {"en": "Age", "mr": "वय", "hi": "आयु"},
    "systolic_bp": {"en": "Systolic BP (mm Hg)", "mr": "सिस्टोलिक बीपी (मिमी एचजी)", "hi": "सिस्टोलिक बीपी (मिमी एचजी)"},
    "diastolic_bp": {"en": "Diastolic BP (mm Hg)", "mr": "डायस्टोलिक बीपी (मिमी एचजी)", "hi": "डायस्टोलिक बीपी (मिमी एचजी)"},
    "bs": {"en": "Blood Sugar (mmol/L)", "mr": "रक्त शर्करा (mmol/L)", "hi": "रक्त शर्करा (mmol/L)"},
    "body_temp": {"en": "Body Temperature (°F)", "mr": "शरीराचे तापमान (°F)", "hi": "शरीर का तापमान (°F)"},
    "heart_rate": {"en": "Heart Rate (bpm)", "mr": "हृदय गती (bpm)", "hi": "हृदय गति (bpm)"},
    "assess_button": {"en": "Assess Risk Level", "mr": "जोखीम पातळी तपासा", "hi": "जोखिम स्तर का आकलन करें"},
    "result_header": {"en": "Assessment Result", "mr": "मूल्यांकन परिणाम", "hi": "मूल्यांकन परिणाम"},
    "outcome_prefix": {"en": "Outcome", "mr": "परिणाम", "hi": "परिणाम"},
    "low_risk_rec": {"en": "Recommendation: Low risk detected. Continue with regular check-ups.", "mr": "शिफारस: कमी जोखीम आढळली. नियमित तपासणी सुरू ठेवा.", "hi": "सिफारिश: कम जोखिम का पता चला। नियमित जांच जारी रखें।"},
    "mid_risk_rec": {"en": "Recommendation: Medium risk detected. Please schedule a consultation with a doctor.", "mr": "शिफारस: मध्यम जोखीम आढळली. कृपया डॉक्टरांचा सल्ला घ्या.", "hi": "सिफारिश: मध्यम जोखिम का पता चला। कृपया डॉक्टर से परामर्श के लिए समय निर्धारित करें।"},
    "high_risk_rec": {"en": "Recommendation: High risk detected. Please seek immediate medical attention.", "mr": "शिफारस: उच्च जोखीम आढळली. कृपया तात्काळ वैद्यकीय मदत घ्या.", "hi": "सिफारिश: उच्च जोखिम का पता चला। कृपया तत्काल चिकित्सा सहायता लें।"},
    
    # Disease Prediction
    "disease_title": {"en": "🩺 General Disease Predictor", "mr": "🩺 सर्वसाधारण रोग निदान", "hi": "🩺 सामान्य रोग निदान"},
    "disease_desc": {"en": "Select the symptoms the patient is experiencing to get a preliminary diagnosis.", "mr": "प्राथमिक निदान मिळविण्यासाठी रुग्ण अनुभवत असलेली लक्षणे निवडा.", "hi": "प्रारंभिक निदान प्राप्त करने के लिए रोगी द्वारा अनुभव किए जा रहे लक्षणों का चयन करें।"},
    "symptoms_header": {"en": "Select Symptoms", "mr": "लक्षणे निवडा", "hi": "लक्षण चुनें"},
    "symptoms_placeholder": {"en": "Start typing to select symptoms...", "mr": "लक्षणे निवडण्यासाठी टाइप करण्यास सुरुवात करा...", "hi": "लक्षणों का चयन करने के लिए टाइप करना शुरू करें..."},
    "symptoms_help": {"en": "You can select multiple symptoms.", "mr": "तुम्ही एकापेक्षा जास्त लक्षणे निवडू शकता.", "hi": "आप कई लक्षणों का चयन कर सकते हैं।"},
    "predict_button": {"en": "Predict Disease", "mr": "रोगाचे निदान करा", "hi": "रोग का निदान करें"},
    "no_symptom_warn": {"en": "Please select at least one symptom.", "mr": "कृपया किमान एक लक्षण निवडा.", "hi": "कृपया कम से कम एक लक्षण चुनें।"},
    "diagnosis_header": {"en": "Preliminary Diagnosis", "mr": "प्राथमिक निदान", "hi": "प्रारंभिक निदान"},
    "predicted_condition": {"en": "Predicted Condition", "mr": "संभाव्य रोग", "hi": "अनुमानित स्थिति"},
    "disclaimer": {
        "en": "**Disclaimer:** This is a prediction based on symptoms and not a final medical diagnosis. Please consult a qualified doctor for an accurate assessment and treatment.",
        "mr": "**अस्वीकरण:** हे एक लक्षणांवर आधारित निदान आहे आणि अंतिम वैद्यकीय निदान नाही. अचूक मूल्यांकन आणि उपचारांसाठी कृपया पात्र डॉक्टरांचा सल्ला घ्या.",
        "hi": "**अस्वीकरण:** यह लक्षणों पर आधारित एक भविष्यवाणी है और अंतिम चिकित्सा निदान नहीं है। सटीक मूल्यांकन और उपचार के लिए कृपया एक योग्य चिकित्सक से परामर्श करें।"
    },
    "analyzing": {"en": "Analyzing...", "mr": "विश्लेषण करत आहे...", "hi": "विश्लेषण हो रहा है..."},
}

# Helper function for translation
def T(key):
    return translations[key][st.session_state.lang]

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
# MODEL & DATA LOADING
# -----------------------------
@st.cache_data
def load_health_models():
    """Load health prediction models and data"""
    try:
        # Try to load models if they exist
        maternal_model = None
        disease_model = None
        disease_encoder = None
        symptom_list = []
        
        if os.path.exists('model/maternal_risk_model.joblib'):
            maternal_model = joblib.load('model/maternal_risk_model.joblib')
        
        if os.path.exists('model/disease_model.joblib'):
            disease_model = joblib.load('model/disease_model.joblib')
        
        if os.path.exists('model/disease_label_encoder.joblib'):
            disease_encoder = joblib.load('model/disease_label_encoder.joblib')
        
        if os.path.exists('database/Training.csv'):
            symptom_data = pd.read_csv('database/Training.csv')
            symptom_list = symptom_data.columns[:-1].tolist()
        else:
            # Default symptom list if CSV is not available
            symptom_list = [
                'itching', 'skin_rash', 'nodal_skin_eruptions', 'continuous_sneezing', 'shivering',
                'chills', 'joint_pain', 'stomach_pain', 'acidity', 'ulcers_on_tongue', 'muscle_wasting',
                'vomiting', 'burning_micturition', 'spotting_urination', 'fatigue', 'weight_gain',
                'anxiety', 'cold_hands_and_feets', 'mood_swings', 'weight_loss', 'restlessness',
                'lethargy', 'patches_in_throat', 'irregular_sugar_level', 'cough', 'high_fever',
                'sunken_eyes', 'breathlessness', 'sweating', 'dehydration', 'indigestion',
                'headache', 'yellowish_skin', 'dark_urine', 'nausea', 'loss_of_appetite',
                'pain_behind_the_eyes', 'back_pain', 'constipation', 'abdominal_pain', 'diarrhoea',
                'mild_fever', 'yellow_urine', 'yellowing_of_eyes', 'acute_liver_failure',
                'fluid_overload', 'swelling_of_stomach', 'swelled_lymph_nodes', 'malaise',
                'blurred_and_distorted_vision', 'phlegm', 'throat_irritation', 'redness_of_eyes',
                'sinus_pressure', 'runny_nose', 'congestion', 'chest_pain', 'weakness_in_limbs',
                'fast_heart_rate', 'pain_during_bowel_movements', 'pain_in_anal_region',
                'bloody_stool', 'irritation_in_anus', 'neck_pain', 'dizziness', 'cramps',
                'bruising', 'obesity', 'swollen_legs', 'swollen_blood_vessels', 'puffy_face_and_eyes',
                'enlarged_thyroid', 'brittle_nails', 'swollen_extremeties', 'excessive_hunger',
                'extra_marital_contacts', 'drying_and_tingling_lips', 'slurred_speech',
                'knee_pain', 'hip_joint_pain', 'muscle_weakness', 'stiff_neck', 'swelling_joints',
                'movement_stiffness', 'spinning_movements', 'loss_of_balance', 'unsteadiness',
                'weakness_of_one_body_side', 'loss_of_smell', 'bladder_discomfort',
                'foul_smell_of_urine', 'continuous_feel_of_urine', 'passage_of_gases',
                'internal_itching', 'toxic_look_(typhos)', 'depression', 'irritability',
                'muscle_pain', 'altered_sensorium', 'red_spots_over_body', 'belly_pain',
                'abnormal_menstruation', 'dischromic_patches', 'watering_from_eyes',
                'increased_appetite', 'polyuria', 'family_history', 'mucoid_sputum',
                'rusty_sputum', 'lack_of_concentration', 'visual_disturbances',
                'receiving_blood_transfusion', 'receiving_unsterile_injections', 'coma',
                'stomach_bleeding', 'distention_of_abdomen', 'history_of_alcohol_consumption',
                'fluid_overload', 'blood_in_sputum', 'prominent_veins_on_calf', 'palpitations',
                'painful_walking', 'pus_filled_pimples', 'blackheads', 'scurring', 'skin_peeling',
                'silver_like_dusting', 'small_dents_in_nails', 'inflammatory_nails', 'blister',
                'red_sore_around_nose', 'yellow_crust_ooze'
            ]
        
        return maternal_model, disease_model, disease_encoder, symptom_list
    except Exception as e:
        st.error(f"Error loading models: {str(e)}")
        return None, None, None, []

# Load models
maternal_model, disease_model, disease_encoder, symptom_list = load_health_models()

# -----------------------------
# SESSION STATE INITIALIZATION
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "prediction_history" not in st.session_state:
    st.session_state.prediction_history = []
if 'lang' not in st.session_state:
    st.session_state.lang = 'en'

# -----------------------------
# SIDEBAR NAVIGATION
# -----------------------------
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='color: #667eea; font-size: 2rem; margin-bottom: 0;'>🩺</h1>
        <h2 style='color: #1e293b; margin-top: 0;'>Health Assistant</h2>
        <p style='color: #64748b; font-size: 0.9rem;'>Complete AI Health Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Language Selection
    lang_map = {"English": "en", "मराठी": "mr", "हिन्दी": "hi"}
    lang_options = list(lang_map.keys())
    reverse_lang_map = {v: k for k, v in lang_map.items()}
    
    current_lang_name = reverse_lang_map[st.session_state.lang]
    current_lang_index = lang_options.index(current_lang_name)
    
    lang_choice = st.selectbox(
        label=T("language_label"),
        options=lang_options,
        index=current_lang_index
    )
    st.session_state.lang = lang_map[lang_choice]
    
    st.divider()
    
    if st.session_state.logged_in:
        st.success(f"👋 Welcome, {st.session_state.username}!")
    
    # Updated menu with health tools
    menu_options = {
        f"🏠 {T('home_name')}": "Home",
        f"📝 {T('register_name')}": "Register", 
        f"🔐 {T('login_name')}": "Login",
        f"📊 {T('dashboard_name')}": "Dashboard",
        f"👥 {T('users_name')}": "Users",
        f"👩‍⚕️ {T('maternal_tool_name')}": "Maternal Health",
        f"🩺 {T('disease_tool_name')}": "Disease Prediction",
        f"🔍 {T('skin_analysis_name')}": "Image Prediction",
        f"💬 {T('chatbot_name')}": "Chatbot",
        f"ℹ️ {T('about_name')}": "About Us",
        f"🚪 {T('logout_name')}": "Logout"
    }
    
    menu = st.radio("Navigation", list(menu_options.keys()), format_func=lambda x: x)
    menu = menu_options[menu]

# -----------------------------
# HOME PAGE
# -----------------------------
if menu == "Home":
    # Hero Section
    st.markdown(f"""
    <div class='main-header'>
        <h1>🩺 {T("app_title")}</h1>
        <p>Complete AI-Powered Health Analysis Platform - Skin Analysis, Disease Prediction & Maternal Health</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features Section
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class='feature-card'>
            <div class='feature-icon'>👩‍⚕️</div>
            <h3>Maternal Health Risk</h3>
            <p>Assess maternal health risks using vital signs. Perfect for health workers in rural areas.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='feature-card'>
            <div class='feature-icon'>🩺</div>
            <h3>Disease Prediction</h3>
            <p>Get preliminary diagnosis based on symptoms using AI-powered disease prediction models.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='feature-card'>
            <div class='feature-icon'>🔍</div>
            <h3>Skin Analysis</h3>
            <p>Upload skin images for instant AI-powered skin disease detection and analysis.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Second row of features
    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.markdown("""
        <div class='feature-card'>
            <div class='feature-icon'>💬</div>
            <h3>Medical Chatbot</h3>
            <p>Get personalized medical advice and recommendations from our intelligent AI assistant.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown("""
        <div class='feature-card'>
            <div class='feature-icon'>🌐</div>
            <h3>Multilingual Support</h3>
            <p>Available in English, Hindi, and Marathi for better accessibility in rural areas.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col6:
        st.markdown("""
        <div class='feature-card'>
            <div class='feature-icon'>📊</div>
            <h3>Personal Dashboard</h3>
            <p>Track your health analysis history and monitor your health journey over time.</p>
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
# MATERNAL HEALTH RISK PREDICTOR
# -----------------------------
elif menu == "Maternal Health":
    st.markdown(f"""
    <div class='main-header'>
        <h1>{T("maternal_title")}</h1>
        <p>{T("maternal_desc")}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if maternal_model is None:
        st.error("⚠️ Maternal health model not available. Please ensure model files are properly loaded.")
        st.info("This feature requires the maternal risk prediction model to be available.")
    else:
        st.markdown("<div class='info-card'>", unsafe_allow_html=True)
        st.markdown(f"### {T('vitals_header')}")
        
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input(T("age"), 10, 70, 25, 1)
            systolic_bp = st.number_input(T("systolic_bp"), 70, 180, 120, 1)
            diastolic_bp = st.number_input(T("diastolic_bp"), 40, 120, 80, 1)
        with col2:
            bs = st.number_input(T("bs"), 6.0, 19.0, 7.5, 0.1, "%.1f")
            body_temp = st.number_input(T("body_temp"), 96.0, 104.0, 98.6, 0.1, "%.1f")
            heart_rate = st.number_input(T("heart_rate"), 60, 100, 75, 1)

        if st.button(T("assess_button"), use_container_width=True, type="primary"):
            input_data = pd.DataFrame({
                'Age': [age], 
                'SystolicBP': [systolic_bp], 
                'DiastolicBP': [diastolic_bp], 
                'BS': [bs], 
                'BodyTemp': [body_temp], 
                'HeartRate': [heart_rate]
            })
            
            with st.spinner(T("analyzing")):
                time.sleep(1)
                try:
                    prediction = maternal_model.predict(input_data)[0]
                    
                    st.divider()
                    st.markdown(f"### {T('result_header')}")
                    
                    # Risk level translation
                    risk_translation = {"low risk": "Low Risk", "mid risk": "Mid Risk", "high risk": "High Risk"}
                    if st.session_state.lang == "mr":
                        risk_translation = {"low risk": "कमी जोखीम", "mid risk": "मध्यम जोखीम", "high risk": "उच्च जोखीम"}
                    elif st.session_state.lang == "hi":
                        risk_translation = {"low risk": "कम जोखिम", "mid risk": "मध्यम जोखिम", "high risk": "उच्च जोखिम"}

                    if prediction == 'low risk':
                        st.success(f"**{T('outcome_prefix')}: {risk_translation[prediction]}**")
                        st.info(T("low_risk_rec"))
                    elif prediction == 'mid risk':
                        st.warning(f"**{T('outcome_prefix')}: {risk_translation[prediction]}**")
                        st.warning(T("mid_risk_rec"))
                    else:
                        st.error(f"**{T('outcome_prefix')}: {risk_translation[prediction]}**")
                        st.error(T("high_risk_rec"))
                        
                except Exception as e:
                    st.error(f"Error making prediction: {str(e)}")
        
        st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# GENERAL DISEASE PREDICTOR
# -----------------------------
elif menu == "Disease Prediction":
    st.markdown(f"""
    <div class='main-header'>
        <h1>{T("disease_title")}</h1>
        <p>{T("disease_desc")}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if disease_model is None or disease_encoder is None:
        st.error("⚠️ Disease prediction model not available. Please ensure model files are properly loaded.")
        st.info("This feature requires the disease prediction model and encoder to be available.")
    else:
        st.markdown("<div class='info-card'>", unsafe_allow_html=True)
        st.markdown(f"### {T('symptoms_header')}")
        
        selected_symptoms = st.multiselect(
            T("symptoms_placeholder"),
            options=symptom_list,
            help=T("symptoms_help")
        )

        if st.button(T("predict_button"), use_container_width=True, type="primary"):
            if not selected_symptoms:
                st.warning(T("no_symptom_warn"))
            else:
                input_vector = [0] * len(symptom_list)
                for symptom in selected_symptoms:
                    if symptom in symptom_list:
                        input_vector[symptom_list.index(symptom)] = 1
                
                with st.spinner(T("analyzing")):
                    time.sleep(1)
                    try:
                        numeric_prediction = disease_model.predict([input_vector])[0]
                        disease_name = disease_encoder.inverse_transform([numeric_prediction])[0]

                        st.divider()
                        st.markdown(f"### {T('diagnosis_header')}")
                        st.success(f"**{T('predicted_condition')}: {disease_name}**")
                        st.warning(T("disclaimer"))
                        
                        # Store prediction in history
                        prediction_record = {
                            'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                            'type': 'Disease Prediction',
                            'symptoms': selected_symptoms,
                            'prediction': disease_name
                        }
                        st.session_state.prediction_history.append(prediction_record)
                        
                    except Exception as e:
                        st.error(f"Error making prediction: {str(e)}")
        
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