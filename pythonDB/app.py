from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
USER_DIR = os.path.join(PROJECT_ROOT, "User")
IMG_DIR = os.path.join(PROJECT_ROOT, "Img", "mp4")
DATABASE = os.path.join(BASE_DIR, "stocks.db")

app = Flask(__name__, static_folder=USER_DIR, static_url_path="")
CORS(app)

SHOP_PRODUCTS = [
    {"name": "ITECH Lace", "price": 100, "stock": 10, "image": "ITECHlace.png"},
    {"name": "ITECH Sleeveless", "price": 450, "stock": 10, "image": "ITECHSLEEVELES.jpg"},
    {"name": "ITECH T-Shirt", "price": 450, "stock": 10, "image": "ITECHTSHIRT.jpg"},
    {"name": "ORG Shirt", "price": 550, "stock": 10, "image": "ORGSHIRT.png"},
    {"name": "PUP Lace", "price": 100, "stock": 10, "image": "PUPlace.jpg"},
    {"name": "PUP Shirt", "price": 250, "stock": 10, "image": "TANGLAW.webp"},
]


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            price INTEGER NOT NULL DEFAULT 0,
            stock INTEGER NOT NULL DEFAULT 0,
            image TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            buyer_name TEXT NOT NULL,
            buyer_email TEXT NOT NULL,
            buyer_phone TEXT NOT NULL,
            campus TEXT,
            address TEXT,
            city TEXT,
            province TEXT,
            postal TEXT,
            payment_method TEXT,
            payment_details TEXT,
            total INTEGER NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            size TEXT,
            unit_price INTEGER NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        );
    """)

    cols = {row[1] for row in conn.execute("PRAGMA table_info(products)").fetchall()}
    if "price" not in cols:
        conn.execute("ALTER TABLE products ADD COLUMN price INTEGER NOT NULL DEFAULT 0")
    if "image" not in cols:
        conn.execute("ALTER TABLE products ADD COLUMN image TEXT NOT NULL DEFAULT ''")

    count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    old_samples = ("Laptop", "Phone", "Tablet")
    conn.execute(
        f"DELETE FROM products WHERE name IN ({','.join('?' * len(old_samples))})",
        old_samples,
    )

    for p in SHOP_PRODUCTS:
        existing = conn.execute(
            "SELECT id FROM products WHERE name = ?", (p["name"],)
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE products SET price = ?, image = ? WHERE name = ?",
                (p["price"], p["image"], p["name"]),
            )
        else:
            conn.execute(
                "INSERT INTO products (name, price, stock, image) VALUES (?, ?, ?, ?)",
                (p["name"], p["price"], p["stock"], p["image"]),
            )

    conn.commit()
    conn.close()


def row_to_product(row):
    product = dict(row)
    stock = product["stock"]
    if stock == 0:
        product["status"] = "sold_out"
    elif stock >= 999:
        product["status"] = "pre_order"
    elif stock <= 5:
        product["status"] = "low"
    else:
        product["status"] = "ok"
    return product


@app.route("/")
def index():
    return send_from_directory(USER_DIR, "index.html")


@app.route("/img/<path:filename>")
def serve_image(filename):
    return send_from_directory(IMG_DIR, filename)


@app.route("/<path:filename>")
def serve_user_file(filename):
    if os.path.isfile(os.path.join(USER_DIR, filename)):
        return send_from_directory(USER_DIR, filename)
    return jsonify({"error": "Not found"}), 404


@app.route("/api/products", methods=["GET"])
def get_products():
    conn = get_db_connection()
    products = conn.execute("SELECT * FROM products ORDER BY id").fetchall()
    conn.close()
    return jsonify([row_to_product(p) for p in products])


@app.route("/api/products", methods=["POST"])
def create_product():
    data = request.json or {}
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO products (name, price, stock, image) VALUES (?, ?, ?, ?)",
            (data["name"], data.get("price", 0), data.get("stock", 0), data.get("image", "")),
        )
        conn.commit()
        product = conn.execute(
            "SELECT * FROM products WHERE name = ?", (data["name"],)
        ).fetchone()
        conn.close()
        return jsonify(row_to_product(product)), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Product already exists"}), 400


@app.route("/api/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    data = request.json or {}
    conn = get_db_connection()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    if not product:
        conn.close()
        return jsonify({"error": "Product not found"}), 404

    stock = data.get("stock", product["stock"])
    conn.execute("UPDATE products SET stock = ? WHERE id = ?", (stock, product_id))
    conn.commit()
    updated = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    conn.close()
    return jsonify(row_to_product(updated))


@app.route("/api/products/<int:product_id>/sold-out", methods=["PUT"])
def mark_sold_out(product_id):
    conn = get_db_connection()
    conn.execute("UPDATE products SET stock = 0 WHERE id = ?", (product_id,))
    conn.commit()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    conn.close()
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(row_to_product(product))


@app.route("/api/products/<int:product_id>/pre-order", methods=["PUT"])
def mark_pre_order(product_id):
    conn = get_db_connection()
    conn.execute("UPDATE products SET stock = 999 WHERE id = ?", (product_id,))
    conn.commit()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    conn.close()
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(row_to_product(product))


@app.route("/api/products/<int:product_id>/restock", methods=["PUT"])
def restock_product(product_id):
    data = request.json or {}
    amount = data.get("stock", 10)
    conn = get_db_connection()
    conn.execute("UPDATE products SET stock = ? WHERE id = ?", (amount, product_id))
    conn.commit()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    conn.close()
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(row_to_product(product))


@app.route("/api/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    return "", 204


@app.route("/api/orders", methods=["GET"])
def get_orders():
    conn = get_db_connection()
    orders = conn.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
    result = []
    for order in orders:
        items = conn.execute(
            "SELECT * FROM order_items WHERE order_id = ?", (order["id"],)
        ).fetchall()
        o = dict(order)
        o["items"] = [dict(i) for i in items]
        result.append(o)
    conn.close()
    return jsonify(result)


@app.route("/api/orders", methods=["POST"])
def create_order():
    data = request.json or {}
    items = data.get("items", [])
    if not items:
        return jsonify({"error": "Cart is empty"}), 400

    conn = get_db_connection()
    try:
        for item in items:
            product = conn.execute(
                "SELECT * FROM products WHERE name = ?", (item["name"],)
            ).fetchone()
            if not product:
                raise ValueError(f"Product not found: {item['name']}")
            qty = int(item.get("qty", 1))
            stock = product["stock"]
            if stock == 0:
                raise ValueError(f"{product['name']} is sold out")
            if stock < 999 and qty > stock:
                raise ValueError(f"Not enough stock for {product['name']}")

        total = sum(int(i["price"]) * int(i["qty"]) for i in items)
        now = datetime.now().isoformat()
        cursor = conn.execute(
            """INSERT INTO orders
               (buyer_name, buyer_email, buyer_phone, campus, address, city,
                province, postal, payment_method, payment_details, total, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                data.get("buyer_name", ""),
                data.get("buyer_email", ""),
                data.get("buyer_phone", ""),
                data.get("campus", ""),
                data.get("address", ""),
                data.get("city", ""),
                data.get("province", ""),
                data.get("postal", ""),
                data.get("payment_method", ""),
                data.get("payment_details", ""),
                total,
                now,
            ),
        )
        order_id = cursor.lastrowid

        for item in items:
            product = conn.execute(
                "SELECT * FROM products WHERE name = ?", (item["name"],)
            ).fetchone()
            qty = int(item["qty"])
            if product["stock"] < 999:
                conn.execute(
                    "UPDATE products SET stock = stock - ? WHERE id = ?",
                    (qty, product["id"]),
                )
            conn.execute(
                """INSERT INTO order_items
                   (order_id, product_id, product_name, quantity, size, unit_price)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    order_id,
                    product["id"],
                    item["name"],
                    qty,
                    item.get("size", "Default"),
                    int(item["price"]),
                ),
            )

        conn.commit()
        order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
        order_items = conn.execute(
            "SELECT * FROM order_items WHERE order_id = ?", (order_id,)
        ).fetchall()
        conn.close()
        result = dict(order)
        result["items"] = [dict(i) for i in order_items]
        return jsonify(result), 201
    except ValueError as e:
        conn.rollback()
        conn.close()
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({"error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    init_db()
    print("SmartCampus server running at http://localhost:5000")
    print("Admin panel: http://localhost:5000/stocks.html")
    app.run(debug=True, host="0.0.0.0", port=5000)
