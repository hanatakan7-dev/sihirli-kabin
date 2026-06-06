from flask import Blueprint, render_template, request, redirect, session
from flask_bcrypt import Bcrypt

from utils.db import get_db

auth = Blueprint("auth", __name__)

bcrypt = Bcrypt()

# ---------------- REGISTER ---------------- #

@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]

        hashed = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")

        conn = get_db()

        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed)
        )

        conn.commit()

        conn.close()

        return redirect("/login")

    return render_template("register.html")

# ---------------- LOGIN ---------------- #

@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]

        conn = get_db()

        cursor = conn.cursor()

        user = cursor.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()

        conn.close()

        if user and bcrypt.check_password_hash(
            user["password"],
            password
        ):

            session["user"] = username

            return redirect("/")

        else:
            return "Hatalı giriş"

    return render_template("login.html")

# ---------------- LOGOUT ---------------- #

@auth.route("/logout")
def logout():

    session.clear()

    return redirect("/")