# SmartCampus Setup

## Quick Start

```bash
cd pythonDB
pip install -r requirements.txt
python app.py
```

Open **http://localhost:5000**

## Pages

| Page | URL |
|------|-----|
| Home | http://localhost:5000/ |
| Shop | http://localhost:5000/shop.html |
| Tasks | http://localhost:5000/task.html |
| Login | http://localhost:5000/loginsignup.html |
| Stock Control | http://localhost:5000/stocks.html |
| About | http://localhost:5000/about.html |

## Python Database (SQLite)

All data is stored in `pythonDB/stocks.db`:

- **users** — accounts (signup/login persist after browser close)
- **products** — shop inventory
- **orders** — purchases with buyer info
- **events** — campus events from home page
- **tasks** — officer task assignments

Demo account: `demo@campusshop.com` / `123456`

Delete `stocks.db` and restart to reset all data.
