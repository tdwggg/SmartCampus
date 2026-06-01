# Stock Control Database Setup

This project now uses a Python Flask backend with SQLite database instead of localStorage.

## Setup Instructions

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Flask App
```bash
python app.py
```

The Flask server will start on `http://localhost:5000` and automatically create the `stocks.db` database on first run with sample data:
- Laptop (15 units)
- Phone (25 units)
- Tablet (10 units)

### 3. Open Stock Control Panel
Open `stocks.html` in your browser. The page will automatically connect to the Flask API to load and manage stock data.

## API Endpoints

- **GET** `/api/products` - Get all products
- **POST** `/api/products` - Create new product
  - Body: `{"name": "Product Name", "stock": 10}`
- **PUT** `/api/products/<id>` - Update product stock
  - Body: `{"stock": 20}`
- **PUT** `/api/products/<id>/sold-out` - Mark as sold out (stock = 0)
- **PUT** `/api/products/<id>/pre-order` - Mark as pre-order (stock = 999)
- **DELETE** `/api/products/<id>` - Delete product

## Database File
The SQLite database is stored as `stocks.db` in the project directory. Delete this file to reset to initial data.

## Troubleshooting
- If you see "Failed to connect to database" error, make sure the Flask app is running on port 5000
- Check browser console (F12) for any JavaScript errors
