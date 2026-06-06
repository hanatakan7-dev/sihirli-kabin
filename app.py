from flask import Flask, render_template, redirect, session, request
from flask_bcrypt import Bcrypt
from PIL import Image
from werkzeug.utils import secure_filename

import os
import uuid

# AI
from ai.pose_detector import detect_pose
from ai.body_measure import calculate_body

# ROUTES
from routes.main_routes import main
from routes.auth_routes import auth
from routes.cabinet_routes import cabinet
from routes.ai_routes import ai_bp
from routes.camera_routes import camera_bp

# DATABASE
from utils.db import get_db

# --------------------------------------------------
# APP
# --------------------------------------------------

app = Flask(__name__)

app.secret_key = "secret123"

bcrypt = Bcrypt(app)

# --------------------------------------------------
# BLUEPRINTS
# --------------------------------------------------

app.register_blueprint(main)
app.register_blueprint(auth)
app.register_blueprint(cabinet)
app.register_blueprint(ai_bp)
app.register_blueprint(camera_bp)

# --------------------------------------------------
# FOLDERS
# --------------------------------------------------

os.makedirs("static/uploads", exist_ok=True)
os.makedirs("static/results", exist_ok=True)
os.makedirs("static/cloths", exist_ok=True)

# --------------------------------------------------
# DATABASE
# --------------------------------------------------

def init_db():

    conn = get_db()

    cursor = conn.cursor()

    # PRODUCTS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price INTEGER,
        image TEXT,
        cloth_image TEXT
    )
    """)

    # USERS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        is_admin INTEGER DEFAULT 0
    )
    """)

    # ORDERS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        total INTEGER,
        user TEXT
    )
    """)

    # ORDER ITEMS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER
    )
    """)

    # CABINET ITEMS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cabinet_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        product_id INTEGER
    )
    """)

    # DEFAULT PRODUCTS

    cursor.execute("SELECT COUNT(*) FROM products")

    if cursor.fetchone()[0] == 0:

        products = [

            ("Tişört", 150, "tshirt.png", "tshirt.png"),

            ("Pantolon", 300, "pants.png", "pants.png"),

            ("Ayakkabı", 500, "shoes.png", "shoes.png"),

            ("Hoodie", 450, "hoodie_preview.png", "hoodie.png"),

            ("Deri Ceket", 900, "jacket_preview.png", "jacket.png")

        ]

        for p in products:

            cursor.execute("""
            INSERT INTO products (
            name,
            price,
            image,
            cloth_image
            )
            VALUES (?, ?, ?, ?)
            """, p)

    conn.commit()

    conn.close()

# --------------------------------------------------
# CART
# --------------------------------------------------

@app.route("/add/<int:id>")
def add_to_cart(id):

    cart = session.get("cart", {})

    id = str(id)

    cart[id] = cart.get(id, 0) + 1

    session["cart"] = cart

    return redirect("/")


@app.route("/increase/<int:id>")
def increase(id):

    cart = session.get("cart", {})

    id = str(id)

    if id in cart:
        cart[id] += 1

    session["cart"] = cart

    return redirect("/cart")


@app.route("/decrease/<int:id>")
def decrease(id):

    cart = session.get("cart", {})

    id = str(id)

    if id in cart:

        cart[id] -= 1

        if cart[id] <= 0:
            del cart[id]

    session["cart"] = cart

    return redirect("/cart")


@app.route("/remove/<int:id>")
def remove(id):

    cart = session.get("cart", {})

    id = str(id)

    if id in cart:
        del cart[id]

    session["cart"] = cart

    return redirect("/cart")


@app.route("/clear")
def clear():

    session["cart"] = {}

    return redirect("/cart")


@app.route("/cart")
def cart():

    conn = get_db()

    cursor = conn.cursor()

    cart = session.get("cart", {})

    items = []

    total = 0

    for pid, qty in cart.items():

        product = cursor.execute(
            "SELECT * FROM products WHERE id=?",
            (pid,)
        ).fetchone()

        if product:

            subtotal = product["price"] * qty

            total += subtotal

            items.append({

                "id": product["id"],
                "name": product["name"],
                "price": product["price"],
                "image": product["image"],
                "quantity": qty,
                "subtotal": subtotal

            })

    conn.close()

    return render_template(

        "cart.html",

        items=items,

        total=total

    )

# --------------------------------------------------
# CHECKOUT
# --------------------------------------------------

@app.route("/checkout")
def checkout():

    if "user" not in session:
        return redirect("/login")

    conn = get_db()

    cursor = conn.cursor()

    cart = session.get("cart", {})

    total = 0

    for pid, qty in cart.items():

        product = cursor.execute(
            "SELECT * FROM products WHERE id=?",
            (pid,)
        ).fetchone()

        if product:
            total += product["price"] * qty

    cursor.execute(
        "INSERT INTO orders (total, user) VALUES (?, ?)",
        (total, session["user"])
    )

    conn.commit()

    conn.close()

    session["cart"] = {}

    return "Sipariş alındı 🎉"

# --------------------------------------------------
# ADMIN
# --------------------------------------------------

@app.route("/admin")
def admin():

    if "user" not in session:
        return redirect("/login")

    conn = get_db()

    cursor = conn.cursor()

    user = cursor.execute(
        "SELECT * FROM users WHERE username=?",
        (session["user"],)
    ).fetchone()

    if user["is_admin"] != 1:
        return "Yetkisiz"

    products = cursor.execute(
        "SELECT * FROM products"
    ).fetchall()

    orders = cursor.execute(
        "SELECT * FROM orders"
    ).fetchall()

    conn.close()

    return render_template(

        "admin.html",

        products=products,

        orders=orders

    )

# --------------------------------------------------
# ADD PRODUCT
# --------------------------------------------------

@app.route("/add-product", methods=["POST"])
def add_product():

    if "user" not in session:
        return redirect("/login")

    conn = get_db()

    cursor = conn.cursor()

    user = cursor.execute(
        "SELECT * FROM users WHERE username=?",
        (session["user"],)
    ).fetchone()

    if user["is_admin"] != 1:
        return "Yetkisiz"

    name = request.form["name"]

    price = request.form["price"]

    image = request.files["image"]

    filename = secure_filename(image.filename)

    unique_name = f"{uuid.uuid4()}_{filename}"

    save_path = os.path.join(
        "static/uploads",
        unique_name
    )

    image.save(save_path)

    cursor.execute("""
    INSERT INTO products (
    name,
    price,
    image,
    cloth_image
    )
    VALUES (?, ?, ?, ?)
    """, (

        name,
        price,
        unique_name,
        unique_name

    ))

    conn.commit()

    conn.close()

    return redirect("/admin")

# --------------------------------------------------
# DELETE PRODUCT
# --------------------------------------------------

@app.route("/delete-product/<int:id>")
def delete_product(id):

    if "user" not in session:
        return redirect("/login")

    conn = get_db()

    cursor = conn.cursor()

    user = cursor.execute(
        "SELECT * FROM users WHERE username=?",
        (session["user"],)
    ).fetchone()

    if user["is_admin"] != 1:
        return "Yetkisiz"

    product = cursor.execute(
        "SELECT * FROM products WHERE id=?",
        (id,)
    ).fetchone()

    if product:

        image_path = os.path.join(
            "static/uploads",
            product["image"]
        )

        if os.path.exists(image_path):
            os.remove(image_path)

        cursor.execute(
            "DELETE FROM products WHERE id=?",
            (id,)
        )

        conn.commit()

    conn.close()

    return redirect("/admin")

# --------------------------------------------------
# PROFILE
# --------------------------------------------------

@app.route("/profile")
def profile():

    if "user" not in session:
        return redirect("/login")

    conn = get_db()

    cursor = conn.cursor()

    orders = cursor.execute(
        "SELECT * FROM orders WHERE user=?",
        (session["user"],)
    ).fetchall()

    conn.close()

    return render_template(

        "profile.html",

        user=session["user"],

        orders=orders

    )

# --------------------------------------------------
# AI TRYON PAGE
# --------------------------------------------------

@app.route("/try/<int:id>")
def try_page(id):

    conn = get_db()

    cursor = conn.cursor()

    product = cursor.execute(

        "SELECT * FROM products WHERE id=?",

        (id,)

    ).fetchone()

    conn.close()

    if not product:

        return "Ürün bulunamadı"

    session["try_product"] = {

        "id": product["id"],

        "name": product["name"],

        "price": product["price"],

        "image": product["image"],

        "cloth_image": product["cloth_image"]

    }

    return render_template(

        "try.html",

        product=product

    )

# --------------------------------------------------
# AI CAMERA PAGE
# --------------------------------------------------

@app.route("/ai-camera")
def ai_camera():

    product = session.get("try_product")

    if not product:

        return redirect("/")

    return render_template(

        "virtual_fitting.html",

        product=product

    )

# --------------------------------------------------
# AI PROCESS
# --------------------------------------------------

@app.route("/cheap-tryon", methods=["POST"])
def cheap_tryon():

    person = request.files["image"]

    unique_name = f"{uuid.uuid4()}.png"

    person_path = os.path.join(
        "static/uploads",
        unique_name
    )

    result_name = f"result_{unique_name}"

    result_path = os.path.join(
        "static/results",
        result_name
    )

    # SAVE USER IMAGE

    person.save(person_path)

    # AI POSE

    landmarks = detect_pose(

        person_path,

        result_path

    )

    # BODY ANALYSIS

    body_data = calculate_body(

        person_path,

        landmarks

    )

    # GOLD EFFECT

    base = Image.open(
        result_path
    ).convert("RGBA")

    overlay = Image.new(

        "RGBA",

        base.size,

        (255, 215, 0, 30)

    )

    result = Image.alpha_composite(

        base,

        overlay

    )

    result.save(result_path)

    return render_template(

        "result.html",

        result="/" + result_path,

        body_data=body_data,

        landmarks=landmarks

    )

# --------------------------------------------------
# MAKE ADMIN
# --------------------------------------------------

@app.route("/make-admin")
def make_admin():

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute(
        "UPDATE users SET is_admin=1 WHERE username='atakan'"
    )

    conn.commit()

    conn.close()

    return "Admin yapıldı"

# --------------------------------------------------
# RUN
# --------------------------------------------------

if __name__ == "__main__":

    init_db()

    app.run(debug=True)