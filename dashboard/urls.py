"""
Dashboard URLs Configuration
Expense Tracker & Budget Planner
"""

from django.urls import path
from . import views

urlpatterns = [
    # Main Dashboard
    path('summary/', views.dashboard_summary, name='dashboard_summary'),
    
    # Analytics Endpoints
    path('analytics/trends/', views.spending_trends, name='spending_trends'),
    path('analytics/category-breakdown/', views.category_breakdown, name='category_breakdown'),
    path('analytics/budget-adherence/', views.budget_adherence, name='budget_adherence'),
    path('analytics/month-comparison/', views.month_comparison, name='month_comparison'),
    path('analytics/statistics/', views.expense_statistics, name='expense_statistics'),
]

# localhost:8000/api/dashboard/summary/ -> Dashboard summary endpoint
# localhost:8000/api/dashboard/analytics/trends/ -> Spending trends endpoint
# localhost:8000/api/dashboard/analytics/category-breakdown/ -> Category breakdown endpoint
# localhost:8000/api/dashboard/analytics/budget-adherence/ -> Budget adherence endpoint
# localhost:8000/api/dashboard/analytics/month-comparison/ -> Month comparison endpoint
# localhost:8000/api/dashboard/analytics/statistics/ -> Expense statistics endpoint