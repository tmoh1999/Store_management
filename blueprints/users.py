from flask import Blueprint, render_template, request, redirect, url_for,session,flash
from models import db2, User
from werkzeug.security import generate_password_hash, check_password_hash
users_bp = Blueprint('users', __name__, url_prefix='/users')

@users_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists!")
            return redirect(url_for("users.register"))

        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password=hashed_pw)
        db2.session.add(new_user)
        db2.session.commit()
        flash("Registration successful! Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")

@users_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user"] = username
            session["user_id"] = user.id
            flash("Login successful!")
            return redirect(url_for("users.dashboard"))
        else:
            flash("Invalid username or password")
            return redirect(url_for("users.login"))

    return render_template("login.html")

@users_bp.route("/dashboard")
def dashboard():
    if "user" not in session: return redirect(url_for("users.login"))
    return render_template("index.html", username=session["user"])

@users_bp.route("/logout")
def logout():
    session.pop("user", None)
    flash("You have been logged out.")
    return redirect(url_for("users.login"))
