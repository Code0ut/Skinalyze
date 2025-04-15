from flask import Flask, render_template, redirect, url_for, flash, request,jsonify  # Import necessary modules
import requests
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models import db, User
from forms import RegisterForm, LoginForm
import os
from gradio_client import Client, handle_file

app = Flask(__name__)  # Initialize the Flask application

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Configure the database URI

app.config['SECRET_KEY'] = 'supersecretkey'

db.init_app(app)  # Initialize the database with the app

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader  # Load user for login management

def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.route("/")  # Route for the index page

def index():
    return render_template("dashboard0.html")
    
@app.route("/register", methods=["GET", "POST"])  # Route for user registration
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash("Username already exists. Please choose a different one.", "danger")
            return redirect(url_for("register"))

        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data,email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])  # Route for user login
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Get the user by username
        user = User.query.filter_by(username=form.username.data).first()

        # If user exists and password is correct
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)  # Log the user in
            return redirect(url_for("dashboard"))  # Redirect to the dashboard

        flash("Login failed. Check username and password.", "danger")

    return render_template("login.html", form=form)


@app.route("/dashboard")  # Route for the user dashboard

@login_required
def dashboard():
    return render_template("dashboard.html", username=current_user.username, email=current_user.email)

@app.route("/logout")  # Route for user logout

@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/users")  # Route for displaying registered users

@login_required
def users():
    all_users = User.query.all()
    return render_template("users.html", users=all_users)

@app.route("/image_form")
def image_form():
    return render_template("image_form.html")




@app.route("/predict_image", methods=["POST"])
def predict_image():
    if 'image' not in request.files or request.files['image'].filename == '':
        return jsonify({"error": "No image uploaded or empty filename"}), 400

    image_file = request.files['image']
    image_path = os.path.join("temp", image_file.filename)

    # Ensure the 'temp' directory exists
    if not os.path.exists("temp"):
        os.makedirs("temp")

    image_file.save(image_path)

    try:
        client = Client("Hrigved/skinalyze")
        result = client.predict(
            image=handle_file(image_path),
            api_name="/predict"
        )

        # Assuming result is a dictionary with a 'prediction' key
        prediction = result.get('label', 'No prediction available')
        confidences=result.get('confidences','no confidences')
        os.remove(image_path)  # Clean up temp file
        return jsonify({"prediction": prediction,
                        "confidences":confidences
                        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/chatbot_form")
def chatbot_form():
    return render_template("chatbot.html")


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    global primary_symptom0,location0,associated_symptoms0,duration0,severity0,additional_info0
    result = None
    if request.method == 'POST':
        primary_symptom0 = request.form['primary_symptom']
        location0 = request.form['location']
        associated_symptoms0 = request.form['associated_symptoms']
        duration0 = request.form['duration']
        severity0 = request.form['severity']
        additional_info0 = request.form['additional_info']

    from gradio_client import Client

    client = Client("Pro-Coder/Skinalyze")
    result = client.predict(
        primary_symptom=primary_symptom0,
        location=location0,
        associated_symptoms=associated_symptoms0,
        duration=duration0,
        severity=severity0,
        additional_info=additional_info0,
        api_name="/predict"
    )
    return jsonify(result)

@app.route("/about_us")
def aboutus():
    return render_template("aboutUs.html")

if __name__ == "__main__":  # Run the application

    with app.app_context():
        db.create_all()
    app.run(debug=True)
