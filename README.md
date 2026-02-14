# Expense Tracker API (Django REST Framework)

This repository contains the backend for an expense tracking application built with Django and Django REST Framework. It provides APIs for managing accounts, budgets, expenses, contacts, dashboards, and user settings.

## 📁 Project structure

The Django project is located in the `proj_expense_track` directory with several apps:

- `account` – user account and authentication functionality
- `api_budgets` – budget management APIs
- `api_expenses` – expense tracking APIs
- `contact` – contact management
- `dashboard` – analytics and dashboard views
- `usersettings` – user preferences and settings

## 🚀 Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/codebyrishi3075/SDLC-Group-Project-Expense-Tracked-API-USING-DRF-Enhanced.git
   cd proj_expense_track
   ```

2. **Create virtual environment & install dependencies**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```

3. **Apply migrations and seed initial data**
   ```bash
   python manage.py migrate
   python manage.py loaddata initial_data.json  # if provided
   ```

4. **Run the development server**
   ```bash
   python manage.py runserver
   ```

5. **Access API**
   Visit `http://127.0.0.1:8000/` and use the included Postman collection (`Expense Tracker API3.postman_collection.json`) to explore endpoints.

## 🔒 Configuration

- Environment variables (e.g., `SECRET_KEY`, database settings) can be managed with a `.env` file or your preferred method.

## 📝 Documentation

See the `React Setup Guide` and `Readme Documents` directories for API documentation, frontend integration guides, and other project notes.

## 📦 Included Files

- `db.sqlite3` – local SQLite database (should be ignored in git)
- `requirements.txt` – Python package list
- Postman collection for API testing

## ✨ Contributing

Contributions are welcome! Please open issues or pull requests with improvements.

## 📄 License

[Specify license if applicable]
