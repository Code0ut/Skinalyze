from flask import Flask, render_template, redirect, url_for, flash, request,jsonify  # Import necessary modules
import requests
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models import db, User
from forms import RegisterForm, LoginForm

app = Flask(__name__)  # Initialize the Flask application

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Configure the database URI

app.config['SECRET_KEY'] = 'supersecretkey'

db.init_app(app)  # Initialize the database with the app

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader  # Load user for login management

def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")  # Route for the index page

def index():
    return render_template("dashboard.html")
    
@app.route("/register", methods=["GET", "POST"])  # Route for user registration
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash("Username already exists. Please choose a different one.", "danger")
            return redirect(url_for("register"))

        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])  # Route for user login

def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for("dashboard"))
        else:
            flash("Login failed. Check username and password.", "danger")
    return render_template("login.html", form=form)

@app.route("/dashboard")  # Route for the user dashboard

@login_required
def dashboard():
    return render_template("dashboard.html", username=current_user.username)

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


if __name__ == "__main__":  # Run the application

    with app.app_context():
        db.create_all()
    app.run(debug=True)
