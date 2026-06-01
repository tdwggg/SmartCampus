from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

DATABASE = 'stocks.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with a stocks table"""
    if not os.path.exists(DATABASE):
        conn = get_db_connection()
        conn.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                stock INTEGER NOT NULL
            )
        ''')
        # Add some sample data
        conn.execute("INSERT INTO products (name, stock) VALUES (?, ?)", ("Laptop", 15))
        conn.execute("INSERT INTO products (name, stock) VALUES (?, ?)", ("Phone", 25))
        conn.execute("INSERT INTO products (name, stock) VALUES (?, ?)", ("Tablet", 10))
        conn.commit()
        conn.close()

@app.route('/api/products', methods=['GET'])
def get_products():
    """Fetch all products"""
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return jsonify([dict(p) for p in products])

@app.route('/api/products', methods=['POST'])
def create_product():
    """Create a new product"""
    data = request.json
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO products (name, stock) VALUES (?, ?)',
                    (data['name'], data['stock']))
        conn.commit()
        product = conn.execute('SELECT * FROM products WHERE name = ?',
                              (data['name'],)).fetchone()
        conn.close()
        return jsonify(dict(product)), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Product already exists'}), 400

@app.route('/api/products/<int:id>', methods=['PUT'])
def update_product(id):
    """Update product stock"""
    data = request.json
    conn = get_db_connection()
    conn.execute('UPDATE products SET stock = ? WHERE id = ?',
                (data['stock'], id))
    conn.commit()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone()
    conn.close()
    return jsonify(dict(product))

@app.route('/api/products/<int:id>/sold-out', methods=['PUT'])
def mark_sold_out(id):
    """Mark product as sold out"""
    conn = get_db_connection()
    conn.execute('UPDATE products SET stock = 0 WHERE id = ?', (id,))
    conn.commit()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone()
    conn.close()
    return jsonify(dict(product))

@app.route('/api/products/<int:id>/pre-order', methods=['PUT'])
def mark_pre_order(id):
    """Mark product as pre-order"""
    conn = get_db_connection()
    conn.execute('UPDATE products SET stock = 999 WHERE id = ?', (id,))
    conn.commit()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone()
    conn.close()
    return jsonify(dict(product))

@app.route('/api/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    """Delete a product"""
    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return '', 204

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
