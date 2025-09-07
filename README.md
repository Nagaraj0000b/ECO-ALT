# 🌱 ECO-ALT API

AI-powered eco-friendliness scoring backend for product analysis, alternative recommendations, user management, analytics, and more.

---

## 🚀 Features

- *AI-Powered Analysis:* Google Gemini integration for intelligent product evaluation
- *Comprehensive Scoring:* Multi-dimensional eco-scoring system
- *Alternative Discovery:* Smart recommendations for eco-friendly products
- *User Management:* Complete authentication and authorization system
- *Search & Discovery:* Advanced filtering and search capabilities
- *Analytics & Reporting:* Detailed insights and usage statistics
- *Admin Dashboard:* System management and monitoring tools

---

## 🏗 Project Structure


src/
├── main.py           # FastAPI application entry point
├── routes/
│   ├── auth.py       # Authentication endpoints
│   ├── items.py      # Product analysis endpoints
│   ├── search.py     # Search endpoints
│   ├── analytics.py  # Analytics endpoints
│   ├── admin.py      # Admin endpoints
│   ├── utils.py      # Utility endpoints
│   └── files.py      # File management endpoints
├── models/           # Pydantic models
├── middleware/       # Custom middleware
├── services/         # External service integrations
├── config/           # Configuration management
└── utils/            # Helper functions


---

## 🔑 Authentication

Most endpoints require JWT authentication. Register and login to obtain your access token.

- *Free Tier:* 20 requests/hour
- *Premium Tier:* 100 requests/hour
- *Enterprise Tier:* 1000 requests/hour

---

## 📚 API Endpoints

### Public Endpoints

| Method | Path         | Description                        |
|--------|--------------|------------------------------------|
| GET    | /ping      | Health check                       |
| GET    | /info      | Application info                   |
| POST   | /analyze   | Legacy product analysis            |
| GET    | /docs      | Swagger UI                         |
| GET    | /redoc     | ReDoc documentation                |

---

### Utility Endpoints (utils.router)

| Method | Path              | Description                    |
|--------|-------------------|-------------------------------|
| GET    | /health         | Health status                 |
| GET    | /status         | Server status                 |
| GET    | /feedback       | Submit feedback               |

---

### Authentication Endpoints (auth.router)

| Method | Path                        | Description                    |
|--------|-----------------------------|-------------------------------|
| POST   | /api/auth/register        | Register new user             |
| POST   | /api/auth/login           | Login and get JWT token       |
| GET    | /api/auth/me              | Get current user info         |
| POST   | /api/auth/logout          | Logout user                   |
| POST   | /api/auth/refresh         | Refresh JWT token             |
| POST   | /api/auth/password-reset  | Request password reset        |

---

### Product/Item Endpoints (items.router)

| Method | Path                        | Description                    |
|--------|-----------------------------|-------------------------------|
| POST   | /api/items/               | Analyze product                |
| GET    | /api/items/{item_id}      | Get product by ID              |
| GET    | /api/items/alternatives   | Get eco-friendly alternatives  |
| GET    | /api/items/score/{item_id}| Get eco-score for product      |
| GET    | /api/items/list           | List all products              |

---

### Search Endpoints (search.router)

| Method | Path                        | Description                    |
|--------|-----------------------------|-------------------------------|
| GET    | /api/search/              | Search products                |
| GET    | /api/search/alternatives  | Search for alternatives        |
| GET    | /api/search/categories    | List product categories        |

---

### Analytics Endpoints (analytics.router)

| Method | Path                        | Description                    |
|--------|-----------------------------|-------------------------------|
| GET    | /api/analytics/usage      | Usage statistics               |
| GET    | /api/analytics/products   | Product analytics              |
| GET    | /api/analytics/users      | User analytics                 |

---

### Admin Endpoints (admin.router)

| Method | Path                        | Description                    |
|--------|-----------------------------|-------------------------------|
| GET    | /api/admin/users          | List all users                 |
| GET    | /api/admin/products       | List all products              |
| POST   | /api/admin/ban-user       | Ban a user                     |
| POST   | /api/admin/unban-user     | Unban a user                   |
| GET    | /api/admin/stats          | System statistics              |

---

### File Management Endpoints (files.router)

| Method | Path                        | Description                    |
|--------|-----------------------------|-------------------------------|
| POST   | /api/files/upload         | Upload a file                  |
| GET    | /api/files/{file_id}      | Download a file                |
| GET    | /api/files/list           | List uploaded files            |

---

## 🧪 Testing Endpoints

### Interactive Docs

- *Swagger UI:* [http://localhost:8000/docs](http://localhost:8000/docs)
- *ReDoc:* [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Example Requests

*Health Check:*
bash
curl http://localhost:8000/ping


*Register:*
bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "yourpassword"}'


*Analyze Product:*
bash
curl -X POST http://localhost:8000/api/items/ \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Eco Bottle", "category": "Drinkware", "material": "Glass"}'


---

## 🧑‍💻 Development

*Run the server:*
bash
uvicorn src.main:app --reload


*Run tests:*
bash
pytest


---

## 📞 Support

For questions or support, contact [support@ecoalt.com](mailto:support@ecoalt.com) or visit [ecoalt.com/support](https://ecoalt.com/support).

---

*License:* MIT  
*Version:*
