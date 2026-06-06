from flask import Blueprint, session, redirect, render_template

from utils.db import get_db

cabinet = Blueprint("cabinet", __name__)

# ---------------- KABİNE EKLE ---------------- #

@cabinet.route("/add-to-cabinet/<int:id>")
def add_to_cabinet(id):

    if "user" not in session:
        return redirect("/login")

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO cabinet_items (username, product_id) VALUES (?, ?)",
        (session["user"], id)
    )

    conn.commit()

    conn.close()

    return redirect("/cabinet")

# ---------------- KABİNİM ---------------- #

@cabinet.route("/cabinet")
def cabinet_page():

    if "user" not in session:
        return redirect("/login")

    conn = get_db()

    cursor = conn.cursor()

    items = cursor.execute("""
    SELECT products.*
    FROM cabinet_items
    JOIN products
    ON cabinet_items.product_id = products.id
    WHERE cabinet_items.username=?
    """, (session["user"],)).fetchall()

    conn.close()

    return render_template(
        "cabinet.html",
        items=items
    )