from flask import Blueprint, render_template, session
from utils.db import get_db

main = Blueprint("main", __name__)

@main.route("/")
def index():

    conn = get_db()
    cursor = conn.cursor()

    products = cursor.execute(
        "SELECT * FROM products"
    ).fetchall()

    conn.close()

    cart = session.get("cart", {})
    cart_count = sum(cart.values())

    return render_template(
        "index.html",
        products=products,
        cart_count=cart_count
    )