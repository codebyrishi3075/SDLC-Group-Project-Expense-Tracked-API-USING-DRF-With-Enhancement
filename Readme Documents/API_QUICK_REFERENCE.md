# 📱 Quick API Reference Card

## Currency Endpoints

### Get Available Currencies *(Public)*
```
GET /api/usersettings/currencies/
```
**No Auth Required**

```bash
curl http://localhost:8000/api/usersettings/currencies/
```

**Response:**
```json
{
  "data": [
    {"code": "USD", "label": "US Dollar"},
    {"code": "EUR", "label": "Euro"},
    {"code": "INR", "label": "Indian Rupee"},
    ...
  ]
}
```

---

### Get User Settings *(Auth Required)*
```
GET /api/usersettings/
```

```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/usersettings/
```

**Response:**
```json
{
  "data": {
    "currency": "INR",
    "monthly_budget_limit": 50000.00
  }
}
```

---

### Update Currency & Monthly Limit *(Auth Required)*
```
PUT /api/usersettings/update/
```

```bash
curl -X PUT -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"currency": "USD", "monthly_budget_limit": 5000}' \
  http://localhost:8000/api/usersettings/update/
```

**Request:**
```json
{
  "currency": "USD",
  "monthly_budget_limit": 5000.00
}
```

---

## Budget Endpoints

### Create Category
```
POST /api/budgets/create/
```
```bash
curl -X POST -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Travel"}' \
  http://localhost:8000/api/budgets/create/
```

---

### List Categories
```
GET /api/budgets/
```
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/budgets/
```

---

### Create Budget for Month ⭐
```
POST /api/budgets/budgets/create/
```
```bash
curl -X POST -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "category": 1,
    "amount": "2000.00",
    "month": "2026-02-01"
  }' \
  http://localhost:8000/api/budgets/budgets/create/
```

---

### Check Budget Utilization ⭐⭐
```
GET /api/budgets/budgets/utilization/?month=2026-02
```
**Most Important Endpoint!**

```bash
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:8000/api/budgets/budgets/utilization/?month=2026-02"
```

**Response:**
```json
{
  "data": [
    {
      "category_name": "Travel",
      "budget": 2000.00,
      "spent": 1500.00,
      "utilization_percent": 75.0,
      "status": "warning"
    }
  ],
  "summary": {
    "total_budget": 8000.00,
    "total_spent": 3500.00,
    "overall_utilization_percent": 43.75
  },
  "compliance": {
    "total_budget_exceeds_limit": true,
    "message": "Combined budgets exceed limit by 3000.00"
  }
}
```

---

## Status Indicators

| Status | Utilization | Color |
|--------|-------------|-------|
| 🟢 **good** | 0–74% | Green |
| 🟠 **warning** | 75–89% | Orange |
| 🔴 **critical** | 90–99% | Red |
| ⚫ **over_budget** | ≥100% | Dark Red |

---

## Expense Endpoints

### Record Expense
```
POST /api/expenses/create/
```
```bash
curl -X POST -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "category": 1,
    "amount": "150.00",
    "date": "2026-02-14",
    "description": "Flight booking"
  }' \
  http://localhost:8000/api/expenses/create/
```

---

### List Expenses
```
GET /api/expenses/
```

**With Filters:**
```
GET /api/expenses/?category=1&month=2026-02&page=1
```

---

### Export Expenses as PDF
```
GET /api/expenses/expenses/export/pdf/
```

---

## User Account Endpoints

### Register
```
POST /api/account/register/
```
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "user",
    "password": "pass123",
    "confirm_password": "pass123",
    "full_name": "John Doe"
  }' \
  http://localhost:8000/api/account/register/
```

---

### Login
```
POST /api/account/login/
```
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "pass123"
  }' \
  http://localhost:8000/api/account/login/
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com"
  }
}
```
*Save `access` token for authenticated requests*

---

### Verify Email OTP
```
POST /api/account/verify-otp/
```

---

### Get Profile
```
GET /api/account/profile/
```

---

### Update Profile
```
PUT /api/account/profile/update/
```

---

### Password Reset Request
```
POST /api/account/password-reset/request/
```

---

## Dashboard Endpoints

### Dashboard Summary
```
GET /api/dashboard/summary/
```

---

### Spending Trends
```
GET /api/dashboard/analytics/trends/
```

---

### Category Breakdown
```
GET /api/dashboard/analytics/category-breakdown/
```

---

### Budget Adherence
```
GET /api/dashboard/analytics/budget-adherence/
```

---

### Month Comparison
```
GET /api/dashboard/analytics/month-comparison/
```

---

### Expense Statistics
```
GET /api/dashboard/analytics/statistics/
```

---

## Contact & Settings

### Submit Contact Form
```
POST /api/contact/submit/
```
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "email": "john@example.com",
    "subject": "Inquiry",
    "message": "This is a message with at least 10 characters"
  }' \
  http://localhost:8000/api/contact/submit/
```

---

## Common Response Codes

| Code | Meaning |
|------|---------|
| **200** | Success (GET, PUT) |
| **201** | Created (POST) |
| **400** | Bad Request (validation error) |
| **401** | Unauthorized (missing/invalid token) |
| **403** | Forbidden (email not verified) |
| **404** | Not Found |
| **500** | Server Error |

---

## Authentication

All endpoints marked ✅ require authentication.

### Method: Bearer Token (JWT)

**Include in every authenticated request:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Example:**
```bash
curl -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  http://localhost:8000/api/budgets/
```

---

## Date Format

All dates must be in `YYYY-MM-DD` format:

```json
{
  "date": "2026-02-14",
  "month": "2026-02-01"
}
```

---

## Amount Format

All amounts are decimals with 2 decimal places:

```json
{
  "amount": "2000.00",
  "monthly_budget_limit": "50000.00"
}
```

---

## Pagination

List endpoints support pagination:

```
GET /api/expenses/?page=1&limit=20
```

---

## Filtering

Filter by month:
```
GET /api/budgets/budgets/?month=2026-02
GET /api/expenses/?month=2026-02
GET /api/budgets/budgets/utilization/?month=2026-02
```

Filter by category:
```
GET /api/budgets/budgets/?category=1
GET /api/expenses/?category=1
```

---

## Testing

Run all tests:
```bash
python manage.py test account --verbosity=2
```

Expected output:
```
Ran 6 tests in 8.847s
OK
```

---

## Postman Collection

Import the provided Postman collection:
```
Expense Tracker API2 Copy.postman_collection.json
```

All endpoints pre-configured with auth headers and example data.

---

## Documentation Files

- 📄 **IMPLEMENTATION_SUMMARY.md** — Complete overview
- 📄 **CURRENCY_AND_BUDGET_SETUP.md** — Step-by-step with examples
- 📄 **BUDGET_ALLOCATION_GUIDE.md** — Deep dive into logic
- 📄 **BUDGET_FLOW_DIAGRAM.md** — Visual diagrams

---

## Tips

- 💡 Always create categories before allocating budgets
- 💡 Use UTC/ISO dates for consistency
- 💡 Check utilization monthly for warnings
- 💡 Frontend should display status colors from utilization endpoint
- 💡 Currency symbol varies by currency code (USD=$, EUR=€, INR=₹)

---

## Support

Check documentation files for detailed examples and best practices.

All endpoints tested and working ✅

