from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import json
from datetime import datetime

baseDir = os.path.dirname(os.path.abspath(__file__))
projectRoot = os.path.dirname(baseDir)
userDir = os.path.join(projectRoot, "User")
imgDir = os.path.join(projectRoot, "Img", "mp4")
database = os.path.join(baseDir, "stocks.db")

app = Flask(__name__, static_folder=userDir, static_url_path="")
CORS(app)

shopProducts = [
    {"name": "ITECH Lace", "price": 100, "stock": 10, "image": "ITECHlace.png"},
    {"name": "ITECH Sleeveless", "price": 450, "stock": 10, "image": "ITECHSLEEVELES.jpg"},
    {"name": "ITECH T-Shirt", "price": 450, "stock": 10, "image": "ITECHTSHIRT.jpg"},
    {"name": "ORG Shirt", "price": 550, "stock": 10, "image": "ORGSHIRT.png"},
    {"name": "PUP Lace", "price": 100, "stock": 10, "image": "PUPlace.jpg"},
    {"name": "PUP Shirt", "price": 250, "stock": 10, "image": "TANGLAW.webp"},
]


def getDb():
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    return conn


def initDb():
    conn = getDb()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            price INTEGER NOT NULL DEFAULT 0,
            sale_price INTEGER NOT NULL DEFAULT 0,
            on_sale INTEGER NOT NULL DEFAULT 0,
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
            status TEXT NOT NULL DEFAULT 'pending',
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
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organizer_name TEXT NOT NULL,
            event_date TEXT NOT NULL,
            campus TEXT,
            phone TEXT,
            address_line TEXT,
            city TEXT,
            province TEXT,
            postal TEXT,
            event_type TEXT,
            email TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            officer_name TEXT NOT NULL,
            department TEXT NOT NULL,
            position TEXT NOT NULL,
            event_types TEXT NOT NULL,
            description TEXT NOT NULL,
            deadline TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            submission TEXT,
            completed_at TEXT,
            created_at TEXT NOT NULL
        );
    """)

    cols = {row[1] for row in conn.execute("PRAGMA table_info(products)").fetchall()}
    if "price" not in cols:
        conn.execute("ALTER TABLE products ADD COLUMN price INTEGER NOT NULL DEFAULT 0")
    if "sale_price" not in cols:
        conn.execute("ALTER TABLE products ADD COLUMN sale_price INTEGER NOT NULL DEFAULT 0")
    if "on_sale" not in cols:
        conn.execute("ALTER TABLE products ADD COLUMN on_sale INTEGER NOT NULL DEFAULT 0")
    if "image" not in cols:
        conn.execute("ALTER TABLE products ADD COLUMN image TEXT NOT NULL DEFAULT ''")

    orderCols = {row[1] for row in conn.execute("PRAGMA table_info(orders)").fetchall()}
    if "status" not in orderCols:
        conn.execute("ALTER TABLE orders ADD COLUMN status TEXT NOT NULL DEFAULT 'pending'")

    taskCols = {row[1] for row in conn.execute("PRAGMA table_info(tasks)").fetchall()}
    if taskCols and "attachment" not in taskCols:
        conn.execute("ALTER TABLE tasks ADD COLUMN attachment TEXT")

    conn.execute("DELETE FROM products WHERE name IN ('Laptop', 'Phone', 'Tablet')")
    for p in shopProducts:
        row = conn.execute("SELECT id FROM products WHERE name = ?", (p["name"],)).fetchone()
        if row:
            conn.execute(
                "UPDATE products SET price = ?, image = ? WHERE name = ?",
                (p["price"], p["image"], p["name"]),
            )
        else:
            conn.execute(
                "INSERT INTO products (name, price, stock, image) VALUES (?, ?, ?, ?)",
                (p["name"], p["price"], p["stock"], p["image"]),
            )

    demo = conn.execute(
        "SELECT id FROM users WHERE email = ?", ("demo@campusshop.com",)
    ).fetchone()
    if not demo:
        conn.execute(
            "INSERT INTO users (name, email, password, created_at) VALUES (?, ?, ?, ?)",
            (
                "Demo User",
                "demo@campusshop.com",
                generate_password_hash("123456"),
                datetime.now().isoformat(),
            ),
        )

    conn.commit()
    conn.close()


def rowToProduct(row):
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
    product["sale_price"] = product.get("sale_price") or 0
    product["on_sale"] = bool(product.get("on_sale"))
    return product


def rowToOrder(row):
    order = dict(row)
    order["status"] = order.get("status") or "pending"
    return order


def rowToUser(row):
    return {"id": row["id"], "name": row["name"], "email": row["email"]}


def rowToEvent(row):
    return dict(row)


def rowToTask(row):
    task = dict(row)
    task["eventTypes"] = json.loads(task.pop("event_types") or "[]")
    if task.get("submission"):
        task["submission"] = json.loads(task["submission"])
    else:
        task["submission"] = None
    if task.get("attachment"):
        task["attachment"] = json.loads(task["attachment"])
    else:
        task["attachment"] = None
    return task


@app.route("/")
def indexPage():
    return send_from_directory(userDir, "index.html")


@app.route("/img/<path:fileName>")
def serveImage(fileName):
    return send_from_directory(imgDir, fileName)


@app.route("/<path:fileName>")
def serveUserFile(fileName):
    if os.path.isfile(os.path.join(userDir, fileName)):
        return send_from_directory(userDir, fileName)
    return jsonify({"error": "Not found"}), 404


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/api/auth/signup", methods=["POST"])
def authSignup():
    data = request.json or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not name or not email or not password:
        return jsonify({"error": "All fields are required"}), 400
    conn = getDb()
    try:
        conn.execute(
            "INSERT INTO users (name, email, password, created_at) VALUES (?, ?, ?, ?)",
            (name, email, generate_password_hash(password), datetime.now().isoformat()),
        )
        conn.commit()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()
        return jsonify(rowToUser(user)), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Email already registered"}), 400


@app.route("/api/auth/login", methods=["POST"])
def authLogin():
    data = request.json or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    conn = getDb()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid email or password"}), 401
    return jsonify(rowToUser(user))


@app.route("/api/products", methods=["GET"])
def getProducts():
    conn = getDb()
    rows = conn.execute("SELECT * FROM products ORDER BY id").fetchall()
    conn.close()
    return jsonify([rowToProduct(r) for r in rows])


@app.route("/api/products/<int:productId>", methods=["PUT"])
def updateProduct(productId):
    data = request.json or {}
    conn = getDb()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (productId,)).fetchone()
    if not product:
        conn.close()
        return jsonify({"error": "Product not found"}), 404
    stock = data.get("stock", product["stock"])
    price = data.get("price", product["price"])
    sale_price = data.get("sale_price", product["sale_price"])
    if sale_price is None:
        sale_price = product["sale_price"]
    on_sale = data.get("on_sale", product["on_sale"])
    if on_sale is None:
        on_sale = product["on_sale"]
    on_sale = 1 if bool(on_sale) else 0

    conn.execute(
        "UPDATE products SET stock = ?, price = ?, sale_price = ?, on_sale = ? WHERE id = ?",
        (stock, price, sale_price, on_sale, productId),
    )
    conn.commit()
    updated = conn.execute("SELECT * FROM products WHERE id = ?", (productId,)).fetchone()
    conn.close()
    return jsonify(rowToProduct(updated))


@app.route("/api/products/<int:productId>/sold-out", methods=["PUT"])
def markSoldOut(productId):
    conn = getDb()
    conn.execute("UPDATE products SET stock = 0 WHERE id = ?", (productId,))
    conn.commit()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (productId,)).fetchone()
    conn.close()
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(rowToProduct(product))


@app.route("/api/products/<int:productId>/pre-order", methods=["PUT"])
def markPreOrder(productId):
    conn = getDb()
    conn.execute("UPDATE products SET stock = 999 WHERE id = ?", (productId,))
    conn.commit()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (productId,)).fetchone()
    conn.close()
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(rowToProduct(product))


@app.route("/api/products/<int:productId>/restock", methods=["PUT"])
def restockProduct(productId):
    data = request.json or {}
    amount = data.get("stock", 10)
    conn = getDb()
    conn.execute("UPDATE products SET stock = ? WHERE id = ?", (amount, productId))
    conn.commit()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (productId,)).fetchone()
    conn.close()
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(rowToProduct(product))


@app.route("/api/orders", methods=["GET"])
def getOrders():
    conn = getDb()
    orders = conn.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
    result = []
    for order in orders:
        items = conn.execute(
            "SELECT * FROM order_items WHERE order_id = ?", (order["id"],)
        ).fetchall()
        o = rowToOrder(order)
        o["items"] = [dict(i) for i in items]
        result.append(o)
    conn.close()
    return jsonify(result)


@app.route("/api/orders/<int:orderId>/status", methods=["PUT"])
def updateOrderStatus(orderId):
    data = request.json or {}
    status = (data.get("status") or "").strip().lower()
    valid_statuses = {"pending", "shipping", "delivered", "cancelled"}
    if status not in valid_statuses:
        return jsonify({"error": "Invalid order status"}), 400

    conn = getDb()
    order = conn.execute("SELECT * FROM orders WHERE id = ?", (orderId,)).fetchone()
    if not order:
        conn.close()
        return jsonify({"error": "Order not found"}), 404

    conn.execute("UPDATE orders SET status = ? WHERE id = ?", (status, orderId))
    conn.commit()
    updated = conn.execute("SELECT * FROM orders WHERE id = ?", (orderId,)).fetchone()
    conn.close()
    return jsonify(rowToOrder(updated))


@app.route("/api/orders", methods=["POST"])
def createOrder():
    data = request.json or {}
    items = data.get("items", [])
    if not items:
        return jsonify({"error": "Cart is empty"}), 400

    conn = getDb()
    try:
        for item in items:
            product = conn.execute(
                "SELECT * FROM products WHERE name = ?", (item["name"],)
            ).fetchone()
            if not product:
                raise ValueError(f"Product not found: {item['name']}")
            qty = int(item.get("qty", 1))
            if product["stock"] == 0:
                raise ValueError(f"{product['name']} is sold out")
            if product["stock"] < 999 and qty > product["stock"]:
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
        orderId = cursor.lastrowid

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
                    orderId,
                    product["id"],
                    item["name"],
                    qty,
                    item.get("size", "Default"),
                    int(item["price"]),
                ),
            )

        conn.commit()
        order = conn.execute("SELECT * FROM orders WHERE id = ?", (orderId,)).fetchone()
        orderItems = conn.execute(
            "SELECT * FROM order_items WHERE order_id = ?", (orderId,)
        ).fetchall()
        conn.close()
        result = dict(order)
        result["items"] = [dict(i) for i in orderItems]
        return jsonify(result), 201
    except ValueError as e:
        conn.rollback()
        conn.close()
        return jsonify({"error": str(e)}), 400


@app.route("/api/events", methods=["GET"])
def getEvents():
    conn = getDb()
    rows = conn.execute("SELECT * FROM events ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([rowToEvent(r) for r in rows])


@app.route("/api/events", methods=["POST"])
def createEvent():
    data = request.json or {}
    now = datetime.now().isoformat()
    conn = getDb()
    cursor = conn.execute(
        """INSERT INTO events
           (organizer_name, event_date, campus, phone, address_line, city,
            province, postal, event_type, email, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            data.get("organizerName", ""),
            data.get("eventDate", ""),
            data.get("campus", ""),
            data.get("phone", ""),
            data.get("addressLine", ""),
            data.get("city", ""),
            data.get("province", ""),
            data.get("postal", ""),
            data.get("eventType", ""),
            data.get("email", ""),
            now,
        ),
    )
    conn.commit()
    event = conn.execute("SELECT * FROM events WHERE id = ?", (cursor.lastrowid,)).fetchone()
    conn.close()
    return jsonify(rowToEvent(event)), 201


@app.route("/api/events/<int:eventId>", methods=["PUT"])
def updateEvent(eventId):
    data = request.json or {}
    conn = getDb()
    conn.execute(
        """UPDATE events SET organizer_name=?, event_date=?, campus=?, phone=?,
           address_line=?, city=?, province=?, postal=?, event_type=?, email=?
           WHERE id=?""",
        (
            data.get("organizerName", ""),
            data.get("eventDate", ""),
            data.get("campus", ""),
            data.get("phone", ""),
            data.get("addressLine", ""),
            data.get("city", ""),
            data.get("province", ""),
            data.get("postal", ""),
            data.get("eventType", ""),
            data.get("email", ""),
            eventId,
        ),
    )
    conn.commit()
    event = conn.execute("SELECT * FROM events WHERE id = ?", (eventId,)).fetchone()
    conn.close()
    if not event:
        return jsonify({"error": "Event not found"}), 404
    return jsonify(rowToEvent(event))


@app.route("/api/events/<int:eventId>", methods=["DELETE"])
def deleteEvent(eventId):
    conn = getDb()
    conn.execute("DELETE FROM events WHERE id = ?", (eventId,))
    conn.commit()
    conn.close()
    return "", 204


@app.route("/api/tasks", methods=["GET"])
def getTasks():
    conn = getDb()
    rows = conn.execute("SELECT * FROM tasks ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([rowToTask(r) for r in rows])


@app.route("/api/tasks", methods=["POST"])
def createTask():
    data = request.json or {}
    now = datetime.now().isoformat()
    conn = getDb()
    attachment = data.get("attachment")
    attachmentJson = json.dumps(attachment) if attachment else None
    cursor = conn.execute(
        """INSERT INTO tasks
           (officer_name, department, position, event_types, description,
            deadline, status, attachment, created_at)
           VALUES (?, ?, ?, ?, ?, ?, 'pending', ?, ?)""",
        (
            data.get("officerName", ""),
            data.get("department", ""),
            data.get("position", ""),
            json.dumps(data.get("eventTypes", [])),
            data.get("description", ""),
            data.get("deadline", ""),
            attachmentJson,
            now,
        ),
    )
    conn.commit()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (cursor.lastrowid,)).fetchone()
    conn.close()
    return jsonify(rowToTask(task)), 201


@app.route("/api/tasks/<int:taskId>", methods=["PUT"])
def updateTask(taskId):
    data = request.json or {}
    conn = getDb()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (taskId,)).fetchone()
    if not task:
        conn.close()
        return jsonify({"error": "Task not found"}), 404

    status = data.get("status", task["status"])
    submission = data.get("submission")
    completedAt = data.get("completedAt")
    if submission is not None:
        submission = json.dumps(submission)
    else:
        submission = task["submission"]

    conn.execute(
        """UPDATE tasks SET status=?, submission=?, completed_at=? WHERE id=?""",
        (status, submission, completedAt, taskId),
    )
    conn.commit()
    updated = conn.execute("SELECT * FROM tasks WHERE id = ?", (taskId,)).fetchone()
    conn.close()
    return jsonify(rowToTask(updated))


@app.route("/api/tasks/<int:taskId>", methods=["DELETE"])
def deleteTask(taskId):
    conn = getDb()
    conn.execute("DELETE FROM tasks WHERE id = ?", (taskId,))
    conn.commit()
    conn.close()
    return "", 204


if __name__ == "__main__":
    initDb()
    print("SmartCampus server: http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
