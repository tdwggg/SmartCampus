# SmartCampus Setup

## Quick Start

### 1. Install dependencies
```bash
cd pythonDB
pip install -r requirements.txt
```

### 2. Start the server
```bash
python app.py
```

The server runs at **http://localhost:5000** and serves both the website and the database API.

### 3. Open the site
| Page | URL |
|------|-----|
| Home | http://localhost:5000/ |
| Shop | http://localhost:5000/shop.html |
| Admin / Stock Control | http://localhost:5000/stocks.html |
| About | http://localhost:5000/about.html |
| Tasks | http://localhost:5000/task.html |

> Always use the Flask server URL so images and the shop database work correctly.

## Shop & Admin

- **Shop** loads live stock from SQLite via `/api/products`
- **Checkout** saves orders to the database (buyer name, email, items, quantities)
- **Stock Control** (`stocks.html`) lets you restock, mark sold out, set pre-order, and view all orders

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/products` | List all products |
| PUT | `/api/products/<id>` | Update stock |
| PUT | `/api/products/<id>/restock` | Set stock quantity |
| PUT | `/api/products/<id>/sold-out` | Mark sold out |
| PUT | `/api/products/<id>/pre-order` | Mark pre-order |
| GET | `/api/orders` | List all orders |
| POST | `/api/orders` | Place a new order |

## Reset database

Delete `pythonDB/stocks.db` and restart the server to recreate tables with default merchandise.
