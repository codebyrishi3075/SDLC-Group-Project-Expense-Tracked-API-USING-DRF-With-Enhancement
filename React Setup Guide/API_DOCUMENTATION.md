# Expense Tracker API Documentation

## Overview
This is a RESTful API built with Django and Django REST Framework (DRF) for an Expense Tracker application. The API handles user authentication, budget management, expense tracking, and dashboard analytics.

---

## 📋 Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com` (to be configured)

---

## 🔐 Authentication

### Authentication Method
- **Type**: JWT (JSON Web Tokens)
- **Header Format**: `Authorization: Bearer <access_token>`
- **Token Type**: Bearer Token

### Token Details
| Property | Value |
|----------|-------|
| Access Token Lifetime | 7 days |
| Refresh Token Lifetime | 7 days |
| Header Type | Bearer |

### Authentication Flow
1. User registers at `/api/account/register/`
2. User logs in at `/api/account/login/` to receive `access_token` and `refresh_token`
3. Include `access_token` in every authenticated request header
4. When token expires, use `refresh_token` to obtain a new `access_token`

---

## 📌 API Endpoints

### 1. Authentication Endpoints (`/api/account/`)

#### **Register User**
- **Method**: `POST`
- **Endpoint**: `/api/account/register/`
- **Authentication**: Not Required
- **Request Body**:
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "password": "SecurePassword123!",
  "password2": "SecurePassword123!"
}
```
- **Response** (201 Created):
```json
{
  "message": "OTP sent successfully to email"
}
```
- **Error Response** (400):
```json
{
  "message": "Failed to send OTP",
  "error": "Error details here"
}
```

#### **Verify Email OTP**
- **Method**: `POST`
- **Endpoint**: `/api/account/email-verify/`
- **Authentication**: Not Required
- **Request Body**:
```json
{
  "email": "john@example.com",
  "otp": "123456"
}
```
- **Response** (200 OK):
```json
{
  "message": "Email verified successfully",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### **Login**
- **Method**: `POST`
- **Endpoint**: `/api/account/login/`
- **Authentication**: Not Required
- **Request Body**:
```json
{
  "email": "john@example.com",
  "password": "SecurePassword123!"
}
```
- **Response** (200 OK):
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

#### **Refresh Token**
- **Method**: `POST`
- **Endpoint**: `/api/account/token/refresh/`
- **Authentication**: Not Required
- **Request Body**:
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```
- **Response** (200 OK):
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### **Password Reset - Request**
- **Method**: `POST`
- **Endpoint**: `/api/account/password-reset/request/`
- **Authentication**: Not Required
- **Request Body**:
```json
{
  "email": "john@example.com"
}
```
- **Response** (200 OK):
```json
{
  "message": "OTP sent to email successfully"
}
```

#### **Password Reset - Verify OTP**
- **Method**: `POST`
- **Endpoint**: `/api/account/password-reset/verify-otp/`
- **Authentication**: Not Required
- **Request Body**:
```json
{
  "email": "john@example.com",
  "otp": "123456"
}
```
- **Response** (200 OK):
```json
{
  "message": "OTP verified",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### **Password Reset - Confirm**
- **Method**: `POST`
- **Endpoint**: `/api/account/password-reset/confirm/`
- **Authentication**: Required
- **Headers**:
```
Authorization: Bearer <access_token>
```
- **Request Body**:
```json
{
  "new_password": "NewSecurePassword123!",
  "confirm_password": "NewSecurePassword123!"
}
```
- **Response** (200 OK):
```json
{
  "message": "Password reset successfully"
}
```

#### **Get/Update User Profile**
- **Method**: `GET` (retrieve) / `PUT` (update)
- **Endpoint**: `/api/account/profile/`
- **Authentication**: Required
- **Headers**:
```
Authorization: Bearer <access_token>
```
- **Request Body (PUT)**:
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "date_of_birth": "1990-01-01",
  "bio": "User biography",
  "profile_picture": "<image_file>"
}
```
- **Response** (200 OK):
```json
{
  "id": 1,
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "date_of_birth": "1990-01-01",
  "bio": "User biography",
  "profile_picture": "/media/profiles/user1.jpg"
}
```

---

### 2. Budget Endpoints (`/api/budgets/`)

#### **List Budgets**
- **Method**: `GET`
- **Endpoint**: `/api/budgets/`
- **Authentication**: Required
- **Query Parameters**:
  - `search` (optional): Search by category name
  - `ordering` (optional): `-created_at` or `amount`
- **Response** (200 OK):
```json
[
  {
    "id": 1,
    "category": "Food",
    "amount": 5000.00,
    "month": "2025-02",
    "spent": 3200.50,
    "remaining": 1799.50,
    "created_at": "2025-02-01T10:00:00Z",
    "updated_at": "2025-02-05T15:30:00Z"
  }
]
```

#### **Create Budget**
- **Method**: `POST`
- **Endpoint**: `/api/budgets/`
- **Authentication**: Required
- **Request Body**:
```json
{
  "category": "Food",
  "amount": 5000.00,
  "month": "2025-02"
}
```
- **Response** (201 Created):
```json
{
  "id": 1,
  "category": "Food",
  "amount": 5000.00,
  "month": "2025-02",
  "spent": 0,
  "remaining": 5000.00,
  "created_at": "2025-02-01T10:00:00Z",
  "updated_at": "2025-02-01T10:00:00Z"
}
```

#### **Get Budget Details**
- **Method**: `GET`
- **Endpoint**: `/api/budgets/{id}/`
- **Authentication**: Required
- **Response** (200 OK):
```json
{
  "id": 1,
  "category": "Food",
  "amount": 5000.00,
  "month": "2025-02",
  "spent": 3200.50,
  "remaining": 1799.50,
  "created_at": "2025-02-01T10:00:00Z",
  "updated_at": "2025-02-05T15:30:00Z"
}
```

#### **Update Budget**
- **Method**: `PUT`
- **Endpoint**: `/api/budgets/{id}/`
- **Authentication**: Required
- **Request Body**:
```json
{
  "category": "Food",
  "amount": 6000.00,
  "month": "2025-02"
}
```
- **Response** (200 OK):
```json
{
  "id": 1,
  "category": "Food",
  "amount": 6000.00,
  "month": "2025-02",
  "spent": 3200.50,
  "remaining": 2799.50,
  "created_at": "2025-02-01T10:00:00Z",
  "updated_at": "2025-02-05T16:00:00Z"
}
```

#### **Delete Budget**
- **Method**: `DELETE`
- **Endpoint**: `/api/budgets/{id}/`
- **Authentication**: Required
- **Response**: 204 No Content

---

### 3. Expense Endpoints (`/api/expenses/`)

#### **List Expenses**
- **Method**: `GET`
- **Endpoint**: `/api/expenses/`
- **Authentication**: Required
- **Query Parameters**:
  - `search` (optional): Search by description or category
  - `category` (optional): Filter by category
  - `date_from` (optional): Filter from date (YYYY-MM-DD)
  - `date_to` (optional): Filter to date (YYYY-MM-DD)
  - `ordering` (optional): `-created_at`, `amount`, `-amount`
  - `page` (optional): Page number for pagination
- **Response** (200 OK):
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/expenses/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "description": "Groceries",
      "category": "Food",
      "amount": 250.50,
      "date": "2025-02-05",
      "payment_method": "Credit Card",
      "notes": "Weekly groceries",
      "receipt": null,
      "created_at": "2025-02-05T10:00:00Z",
      "updated_at": "2025-02-05T10:00:00Z"
    }
  ]
}
```

#### **Create Expense**
- **Method**: `POST`
- **Endpoint**: `/api/expenses/`
- **Authentication**: Required
- **Request Body**:
```json
{
  "description": "Groceries",
  "category": "Food",
  "amount": 250.50,
  "date": "2025-02-05",
  "payment_method": "Credit Card",
  "notes": "Weekly groceries",
  "receipt": "<image_file>"
}
```
- **Response** (201 Created):
```json
{
  "id": 1,
  "description": "Groceries",
  "category": "Food",
  "amount": 250.50,
  "date": "2025-02-05",
  "payment_method": "Credit Card",
  "notes": "Weekly groceries",
  "receipt": "/media/receipts/receipt1.jpg",
  "created_at": "2025-02-05T10:00:00Z",
  "updated_at": "2025-02-05T10:00:00Z"
}
```

#### **Get Expense Details**
- **Method**: `GET`
- **Endpoint**: `/api/expenses/{id}/`
- **Authentication**: Required
- **Response** (200 OK):
```json
{
  "id": 1,
  "description": "Groceries",
  "category": "Food",
  "amount": 250.50,
  "date": "2025-02-05",
  "payment_method": "Credit Card",
  "notes": "Weekly groceries",
  "receipt": "/media/receipts/receipt1.jpg",
  "created_at": "2025-02-05T10:00:00Z",
  "updated_at": "2025-02-05T10:00:00Z"
}
```

#### **Update Expense**
- **Method**: `PUT`
- **Endpoint**: `/api/expenses/{id}/`
- **Authentication**: Required
- **Request Body**:
```json
{
  "description": "Groceries and Supplies",
  "category": "Food",
  "amount": 300.00,
  "date": "2025-02-05",
  "payment_method": "Debit Card",
  "notes": "Updated weekly groceries"
}
```
- **Response** (200 OK):
```json
{
  "id": 1,
  "description": "Groceries and Supplies",
  "category": "Food",
  "amount": 300.00,
  "date": "2025-02-05",
  "payment_method": "Debit Card",
  "notes": "Updated weekly groceries",
  "receipt": "/media/receipts/receipt1.jpg",
  "created_at": "2025-02-05T10:00:00Z",
  "updated_at": "2025-02-05T11:00:00Z"
}
```

#### **Delete Expense**
- **Method**: `DELETE`
- **Endpoint**: `/api/expenses/{id}/`
- **Authentication**: Required
- **Response**: 204 No Content

---

### 4. Dashboard Endpoints (`/api/dashboard/`)

#### **Get Dashboard Summary**
- **Method**: `GET`
- **Endpoint**: `/api/dashboard/`
- **Authentication**: Required
- **Query Parameters**:
  - `month` (optional): Filter by month (YYYY-MM)
  - `year` (optional): Filter by year (YYYY)
- **Response** (200 OK):
```json
{
  "total_expenses": 5234.75,
  "total_budgets": 15000.00,
  "total_spent": 5234.75,
  "total_remaining": 9765.25,
  "expense_count": 45,
  "budget_count": 8,
  "top_categories": [
    {
      "category": "Food",
      "amount": 1500.00,
      "percentage": 28.5
    },
    {
      "category": "Transportation",
      "amount": 1200.00,
      "percentage": 22.9
    }
  ],
  "monthly_trend": [
    {
      "month": "2025-01",
      "spent": 4500.00
    },
    {
      "month": "2025-02",
      "spent": 5234.75
    }
  ],
  "budget_status": [
    {
      "category": "Food",
      "budget": 5000.00,
      "spent": 1500.00,
      "remaining": 3500.00,
      "percentage_used": 30
    }
  ]
}
```

---

### 5. User Settings Endpoints (`/api/usersettings/`)

#### **Get User Settings**
- **Method**: `GET`
- **Endpoint**: `/api/usersettings/`
- **Authentication**: Required
- **Response** (200 OK):
```json
{
  "id": 1,
  "user": 1,
  "currency": "USD",
  "language": "en",
  "theme": "light",
  "notifications_enabled": true,
  "email_notifications": true,
  "notification_frequency": "weekly",
  "created_at": "2025-02-01T10:00:00Z",
  "updated_at": "2025-02-05T10:00:00Z"
}
```

#### **Update User Settings**
- **Method**: `PUT`
- **Endpoint**: `/api/usersettings/`
- **Authentication**: Required
- **Request Body**:
```json
{
  "currency": "INR",
  "language": "en",
  "theme": "dark",
  "notifications_enabled": true,
  "email_notifications": false,
  "notification_frequency": "monthly"
}
```
- **Response** (200 OK):
```json
{
  "id": 1,
  "user": 1,
  "currency": "INR",
  "language": "en",
  "theme": "dark",
  "notifications_enabled": true,
  "email_notifications": false,
  "notification_frequency": "monthly",
  "created_at": "2025-02-01T10:00:00Z",
  "updated_at": "2025-02-05T11:30:00Z"
}
```

---

## ⚠️ Error Response Format

All error responses follow this format:

**400 Bad Request**:
```json
{
  "field_name": ["Error message"]
}
```

**401 Unauthorized**:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**403 Forbidden**:
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**404 Not Found**:
```json
{
  "detail": "Not found."
}
```

**500 Internal Server Error**:
```json
{
  "detail": "Internal server error"
}
```

---

## 📊 Available Categories for Expenses & Budgets

- Food
- Transportation
- Entertainment
- Utilities
- Healthcare
- Education
- Shopping
- Other

---

## 🔍 Filtering & Search Examples

### List Expenses with Filters
```
GET /api/expenses/?category=Food&date_from=2025-02-01&date_to=2025-02-05&ordering=-amount
```

### Search Expenses
```
GET /api/expenses/?search=groceries
```

### List Budgets for Specific Month
```
GET /api/budgets/?search=Food
```

---

## 📱 Media Files

- **Profile Pictures**: Stored at `/media/profiles/`
- **Receipt Images**: Stored at `/media/receipts/`
- **Supported Formats**: JPG, PNG, GIF
- **Max File Size**: 5MB (to be configured)

---

## 🛠️ Important Notes for Frontend Team

1. **Always include Authorization header** for authenticated endpoints
2. **Token refresh**: Implement token refresh logic when receiving 401 responses
3. **CORS**: The API is configured to accept requests from `http://localhost:3000` in development
4. **Pagination**: The expenses endpoint uses pagination (default 10 items per page)
5. **Date Format**: Use ISO 8601 format (YYYY-MM-DD) for all dates
6. **Time Format**: UTC timezone for all timestamps
7. **File Uploads**: Use FormData for multipart file uploads
8. **Error Handling**: Always check response status and handle errors appropriately
9. **OTP Expiry**: OTP codes expire after a certain period (check backend configuration)
10. **Rate Limiting**: Implement proper retry logic with exponential backoff

---

## 🚀 Additional Resources

- **Postman Collection**: `Expense Tracker API2.postman_collection.json` (included)
- **Django Admin**: `http://localhost:8000/admin` (for backend management)
- **Jazzmin Admin UI**: Better-looking admin interface (already configured)

---

**Last Updated**: February 5, 2026
