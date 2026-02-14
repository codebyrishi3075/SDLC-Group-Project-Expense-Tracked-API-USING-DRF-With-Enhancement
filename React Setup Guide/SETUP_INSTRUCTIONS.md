# Backend Setup Instructions

## 📋 Prerequisites

- Python 3.8+
- pip (Python package manager)
- SQLite3 (included with Python)
- Git

---

## 🚀 Installation Steps

### 1. Clone or Download the Project

```bash
cd path/to/proj_expense_track
```

### 2. Create Virtual Environment

**Windows (PowerShell)**:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS/Linux**:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

First, ensure you have a `requirements.txt` file. If not, create one with:

```bash
pip install django django-rest-framework djangorestframework-simplejwt django-cors-headers python-dotenv django-jazzmin pillow
pip freeze > requirements.txt
```

Then install from requirements.txt:

```bash
pip install -r requirements.txt
```

### 4. Environment Variables Setup

Create a `.env` file in the root directory:

```env
# Django Configuration
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email Configuration (Gmail Example)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
```

**For Gmail Users**:
1. Enable 2-Factor Authentication on Gmail
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use the generated password in `EMAIL_HOST_PASSWORD`

### 5. Database Migrations

```bash
# Apply migrations
python manage.py migrate

# Create superuser (for admin access)
python manage.py createsuperuser
```

### 6. Load Sample Data (Optional)

```bash
python manage.py seed_expenses
```

### 7. Run Development Server

```bash
python manage.py runserver
```

Server will run at: `http://localhost:8000`

---

## 📚 Project Structure Overview

```
proj_expense_track/
├── account/              # User authentication and profiles
├── api_budgets/          # Budget management API
├── api_expenses/         # Expense tracking API
├── dashboard/            # Dashboard statistics API
├── usersettings/         # User settings/preferences API
├── proj_expense_track/   # Main project settings
├── media/                # User uploads (profiles, receipts)
├── db.sqlite3            # Database
├── manage.py             # Django CLI
└── .env                  # Environment variables (CREATE THIS)
```

---

## 🔐 Default Admin Access

After creating superuser:
- **URL**: `http://localhost:8000/admin`
- **Better UI**: `http://localhost:8000/admin` (Jazzmin Admin)

---

## 📦 Main Dependencies

| Package                       | Version | Purpose |
|-------------------------------|---------|---------|
| Django                        | 5.0+    | Web framework |
| djangorestframework           | 3.14+   | REST API |
| djangorestframework-simplejwt | 5.3+    | JWT Authentication |
| django-cors-headers           | 4.3+    | CORS support |
| django-jazzmin                | 2.13+   | Admin UI |
| Pillow                        | 10.0+   | Image processing |
| python-dotenv                 | 1.0+    | Environment variables |

---

## 📝 API Endpoints Reference

### Quick Endpoints Map
```
Authentication:
  POST   /api/account/register/
  POST   /api/account/login/
  POST   /api/account/email-verify/
  POST   /api/account/token/refresh/
  POST   /api/account/password-reset/request/
  POST   /api/account/password-reset/verify-otp/
  POST   /api/account/password-reset/confirm/
  GET/PUT /api/account/profile/

Budgets:
  GET/POST  /api/budgets/
  GET/PUT/DELETE  /api/budgets/{id}/

Expenses:
  GET/POST  /api/expenses/
  GET/PUT/DELETE  /api/expenses/{id}/

Dashboard:
  GET  /api/dashboard/

Settings:
  GET/PUT  /api/usersettings/
```

See `API_DOCUMENTATION.md` for detailed endpoint information.

---

## 🧪 Testing the API

### Using Postman

1. Import the provided Postman collection: `Expense Tracker API2.postman_collection.json`
2. Configure environment variables in Postman
3. Run the collection to test all endpoints

### Using cURL

```bash
# Register
curl -X POST http://localhost:8000/api/account/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "password2": "SecurePass123!"
  }'

# Login
curl -X POST http://localhost:8000/api/account/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'

# Get Expenses (with token)
curl -X GET http://localhost:8000/api/expenses/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🔍 Troubleshooting

### Migration Errors

**Problem**: `ModuleNotFoundError: No module named 'django'`
```bash
# Solution: Activate virtual environment
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate    # macOS/Linux
```

### Database Lock Error

**Problem**: `django.db.utils.OperationalError: database is locked`
```bash
# Solution: Delete database and migrations, then recreate
rm db.sqlite3
rm -rf */migrations/0*.py
python manage.py makemigrations
python manage.py migrate
```

### Port Already in Use

**Problem**: `OSError: [Errno 48] Address already in use`
```bash
# Solution: Use different port
python manage.py runserver 8001
```

### CORS Errors in Frontend

**Problem**: `Access to XMLHttpRequest blocked by CORS policy`
```python
# Solution: In settings.py, ensure CORS_ALLOWED_ORIGINS includes frontend URL
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]
```

### Email Not Sending

**Problem**: `SMTPAuthenticationError`
```python
# Solution: 
# 1. Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in .env
# 2. For Gmail, use App Password, not regular password
# 3. Enable "Less secure app access" if not using 2FA
```

---

## 🛠️ Common Management Commands

```bash
# Create new app
python manage.py startapp app_name

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Run custom command
python manage.py seed_expenses

# Open Django shell
python manage.py shell

# Collect static files (production)
python manage.py collectstatic

# Run tests
python manage.py test

# Check project setup
python manage.py check

# Show all installed apps
python manage.py showmigrations
```

---

## 📊 Database Models Overview

### User Model (Account App)
- Custom user with email as username
- Profile picture support
- Phone number, date of birth fields

### Budget Model (Budget App)
- Category, amount, month
- Automatic spent calculation
- Budget vs actual tracking

### Expense Model (Expense App)
- Description, amount, category
- Payment method tracking
- Receipt image support
- Date filtering support

### User Settings Model (Settings App)
- Currency preference
- Language selection
- Theme (light/dark)
- Notification preferences

### Dashboard (Dashboard App)
- Summary statistics
- Category breakdown
- Monthly trends
- Budget status

---

## 🔐 Security Best Practices

### Development vs Production

**Development** (Current):
```python
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
```

**Production** (To implement):
```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### Additional Security Measures

1. **Use strong SECRET_KEY**: Generate using Django
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

2. **Implement Rate Limiting** (Optional):
   ```bash
   pip install djangorestframework-ratelimit
   ```

3. **Add API Key Authentication** (Optional):
   ```bash
   pip install djangorestframework-api-key
   ```

4. **HTTPS Enforcement** (Production):
   - Use Django's security middleware
   - Configure SSL certificates

---

## 📈 Performance Optimization

### Database Optimization
```python
# Use select_related for foreign keys
# Use prefetch_related for reverse relations
```

### Caching
```bash
# Install Redis cache (optional)
pip install django-redis
```

### Pagination
- Already configured for expenses endpoint
- Default: 10 items per page

---

## 📦 Production Deployment Checklist

- [ ] Set `DEBUG = False`
- [ ] Update `ALLOWED_HOSTS`
- [ ] Generate new `SECRET_KEY`
- [ ] Configure production database (PostgreSQL)
- [ ] Set up environment variables securely
- [ ] Configure static files serving
- [ ] Set up media files storage (AWS S3)
- [ ] Enable HTTPS/SSL
- [ ] Configure CORS for production domain
- [ ] Set up error logging/monitoring
- [ ] Create `.env` file with production secrets
- [ ] Run `python manage.py check --deploy`
- [ ] Set up database backups
- [ ] Configure email backend for production

---

## 🚀 Deployment Options

### 1. **Heroku**
```bash
pip install gunicorn
echo "web: gunicorn proj_expense_track.wsgi" > Procfile
```

### 2. **PythonAnywhere**
- Upload project files
- Configure virtual environment
- Set up web app with WSGI file

### 3. **AWS (EC2 + RDS)**
- Deploy on Ubuntu instance
- Use PostgreSQL for database
- Configure Gunicorn + Nginx

### 4. **DigitalOcean**
- App Platform for easy deployment
- Or manual setup on Droplets

### 5. **Railway.app**
- Connect GitHub repository
- Deploy with one click

---

## 📞 Support & Resources

- **Django Documentation**: https://docs.djangoproject.com/
- **DRF Documentation**: https://www.django-rest-framework.org/
- **JWT Documentation**: https://django-rest-framework-simplejwt.readthedocs.io/

---

**Backend Documentation Version**: 1.0
**Last Updated**: February 5, 2026
**Python Version Required**: 3.8+
**Django Version**: 5.0+
