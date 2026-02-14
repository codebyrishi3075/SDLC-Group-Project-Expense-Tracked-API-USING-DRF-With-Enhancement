from django.urls import path
from . import views
urlpatterns = [
    # Categories
    path('', views.list_categories),
    path('create/', views.create_category),
    path('update/<int:pk>/', views.update_category),
    path('delete/<int:pk>/', views.delete_category),
    
    # Budgets
    path('budgets/', views.list_budgets),
    path('budgets/create/', views.create_budget),
    path('budgets/<int:pk>/update/', views.update_budget),
    path('budgets/<int:pk>/delete/', views.delete_budget),
    path('budgets/utilization/', views.budget_utilization),
]