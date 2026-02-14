from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_expenses),
    path('create/', views.create_expense),
    path('update/<int:pk>/', views.update_expense),
    path('delete/<int:pk>/', views.delete_expense),
    path('expenses/export/pdf/', views.export_expenses_pdf),
]


# locxalhost:8000/api/expenses/ -> List expenses with filtering, search, pagination
# localhost:8000/api/expenses/create/ -> Create new expense
# localhost:8000/api/expenses/update/<id>/ -> Update expense by ID
# localhost:8000/api/expenses/delete/<id>/ -> Delete expense by ID
# localhost:8000/api/expenses/expenses/export/pdf/ -> Export expenses as PDF
