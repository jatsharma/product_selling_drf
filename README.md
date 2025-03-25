# Product Selling Platform

A Django REST Framework based platform for selling products with time-based expiration.

## Setup Instructions

1. Create and activate a virtual environment:
```bash
python -m venv env
source env/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
cd minimal_ecom
python manage.py migrate
```

4. Start the development server:
```bash
python manage.py runserver
```

The server will start at `http://127.0.0.1:8000/`

## API Documentation

### Authentication

All APIs except registration and login require authentication using token-based authentication.

#### Register User
```http
POST /api/register/
Content-Type: application/json

{
    "username": "your_username",
    "email": "your@email.com",
    "first_name": "Your Name",
    "password": "your_password"
}
```

#### Login User
```http
POST /api/login/
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}
```

Both endpoints will return a token that should be included in subsequent requests:
```json
{
    "token": "your_auth_token",
    "user_id": 1,
    "email": "your@email.com",
    "name": "Your Name"
}
```

### Product APIs

All product APIs require authentication. Include the token in the Authorization header:
```
Authorization: Token your_auth_token
```

#### Create Product
```http
POST /api/products/
Content-Type: application/json

{
    "product_name": "Example Product"
}
```

#### List All Products
```http
GET /api/products/
```

#### Get Product by ID
```http
GET /api/products/{id}/
```

#### Buy Product
```http
POST /api/products/{id}/buy/
```

#### List Sold Products
```http
GET /api/products/sold_products/
```

#### List Unsold Products
```http
GET /api/products/unsold_products/
```

### Product Features

- Products expire after 2 minutes from creation time
- Bought products never expire
- All timestamps are in UTC
- Products are ordered by creation date (newest first)
- One product can only be bought once

### Response Format

All product responses include:
```json
{
    "product_id": 1,
    "product_name": "Example Product",
    "created_by": "username",
    "created_at": "2024-03-25T12:00:00Z",
    "bought_time": null,
    "bought_by": null,
    "is_sold": false,
    "is_visible": true
}
```

## Error Responses

- 400 Bad Request: When trying to buy an already sold product
- 401 Unauthorized: When authentication token is missing or invalid
- 404 Not Found: When trying to access an expired or non-existent product