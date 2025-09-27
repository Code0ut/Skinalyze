import streamlit as st
import os
import sqlite3
import bcrypt
from gradio_client import Client, handle_file
from PIL import Image

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
                  password TEXT)''')
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
    c.execute("SELECT username, email FROM users")
    users = c.fetchall()
    conn.close()
    return users

# -----------------------------
# APP LOGIC
# -----------------------------
st.set_page_config(page_title="Skinalyze", layout="wide")

# Session state for authentication
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None

st.sidebar.title("🌐 Skinalyze Navigation")
menu = st.sidebar.radio("Go to", ["Home", "Register", "Login", "Dashboard", "Users", "Image Prediction", "Chatbot", "About Us", "Logout"])

# -----------------------------
# HOME
# -----------------------------
if menu == "Home":
    st.title("Welcome to Skinalyze")
    st.write("AI-powered skin disease detection and chatbot assistance.")

# -----------------------------
# REGISTER
# -----------------------------
elif menu == "Register":
    st.title("Register")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Register"):
        if add_user(username, email, password):
            st.success("Registration successful! Please login.")
        else:
            st.error("Username already exists. Try a different one.")

# -----------------------------
# LOGIN
# -----------------------------
elif menu == "Login":
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = get_user(username)
        if user and bcrypt.checkpw(password.encode('utf-8'), user[3]):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Welcome {username}! Go to Dashboard.")
        else:
            st.error("Invalid username or password.")

# -----------------------------
# DASHBOARD
# -----------------------------
elif menu == "Dashboard":
    if st.session_state.logged_in:
        st.title("User Dashboard")
        st.write(f"👤 Username: {st.session_state.username}")
        user = get_user(st.session_state.username)
        if user:
            st.write(f"📧 Email: {user[2]}")
    else:
        st.warning("Please login first.")

# -----------------------------
# USERS LIST
# -----------------------------
elif menu == "Users":
    if st.session_state.logged_in:
        st.title("Registered Users")
        users = get_all_users()
        st.table(users)
    else:
        st.warning("Please login first.")

# -----------------------------
# IMAGE PREDICTION
# -----------------------------
elif menu == "Image Prediction":
    st.title("Skin Disease Detection")
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image_path = os.path.join("temp", uploaded_file.name)
        if not os.path.exists("temp"):
            os.makedirs("temp")
        with open(image_path, "wb") as f:
            f.write(uploaded_file.read())

        st.image(Image.open(image_path), caption="Uploaded Image", use_column_width=True)

        if st.button("Predict"):
            try:
                client = Client("Hrigved/skinalyze")
                result = client.predict(
                    image=handle_file(image_path),
                    api_name="/predict"
                )
                prediction = result.get('label', 'No prediction available')
                confidences = result.get('confidences', 'No confidences')
                st.success(f"Prediction: {prediction}")
                st.json(confidences)
                os.remove(image_path)
            except Exception as e:
                st.error(f"Error: {str(e)}")

# -----------------------------
# CHATBOT
# -----------------------------
elif menu == "Chatbot":
    st.title("Skinalyze Chatbot")
    with st.form("chat_form"):
        primary_symptom = st.text_input("Primary Symptom")
        location = st.text_input("Location")
        associated_symptoms = st.text_area("Associated Symptoms")
        duration = st.text_input("Duration")
        severity = st.text_input("Severity")
        additional_info = st.text_area("Additional Info")
        submitted = st.form_submit_button("Get Advice")
        if submitted:
            try:
                client = Client("Pro-Coder/Skinalyze")
                result = client.predict(
                    primary_symptom=primary_symptom,
                    location=location,
                    associated_symptoms=associated_symptoms,
                    duration=duration,
                    severity=severity,
                    additional_info=additional_info,
                    api_name="/predict"
                )
                st.json(result)
            except Exception as e:
                st.error(f"Error: {str(e)}")

# -----------------------------
# ABOUT US
# -----------------------------
elif menu == "About Us":
    st.title("About Us")
    st.write("Skinalyze is an AI-powered skin disease detection and chatbot assistance platform built to help users understand their skin health better.")

# -----------------------------
# LOGOUT
# -----------------------------
elif menu == "Logout":
    st.session_state.logged_in = False
    st.session_state.username = None
    st.success("You have been logged out.")

