"""
Dashboard Views - Complete Implementation
Expense Tracker & Budget Planner
Created: February 2026
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Count, Q, Avg, Min, Max
from django.utils import timezone
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from api_expenses.models import Expense
from api_expenses.serializers import ExpenseSerializer
from api_budgets.models import Budget, BudgetCategory
from usersettings.models import UserSettings


# ==================== DASHBOARD SUMMARY API ====================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    """
    Main dashboard summary with all key metrics.
    Returns: Total budget, expenses, category breakdown, recent transactions
    
    Query Parameters:
    - month: YYYY-MM format (default: current month)
    """
    try:
        user = request.user
        
        # Get month from query params or use current month
        month_param = request.GET.get('month', '')
        if month_param:
            try:
                current_month = datetime.strptime(month_param, '%Y-%m').date().replace(day=1)
            except ValueError:
                return Response({
                    'error': 'Invalid month format. Use YYYY-MM',
                    'message': 'Invalid parameter'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            current_month = timezone.now().date().replace(day=1)
        
        # Get current month's expenses
        expenses = Expense.objects.filter(
            user=user,
            date__year=current_month.year,
            date__month=current_month.month
        )
        
        # Total expenses calculation
        total_expenses = expenses.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        # Get budgets for current month
        budgets = Budget.objects.filter(
            user=user,
            month=current_month
        ).select_related('category')
        
        # Total budget calculation
        total_budget = budgets.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        # Calculate remaining and utilization
        remaining = total_budget - total_expenses
        utilization_percent = round(
            (total_expenses / total_budget) * 100, 2
        ) if total_budget > 0 else 0
        
        # Category-wise breakdown
        categories_data = []
        for budget in budgets:
            spent = expenses.filter(
                category=budget.category
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            category_remaining = budget.amount - spent
            category_percent = round(
                (spent / budget.amount) * 100, 2
            ) if budget.amount > 0 else 0
            
            categories_data.append({
                'category_id': budget.category.id,
                'category_name': budget.category.name,
                'budget': float(budget.amount),
                'spent': float(spent),
                'remaining': float(category_remaining),
                'percentage': category_percent,
                'status': 'over_budget' if spent > budget.amount else 'on_track'
            })
        
        # Sort by highest spending
        categories_data.sort(key=lambda x: x['spent'], reverse=True)
        
        # Recent expenses (last 10)
        recent_expenses = expenses.select_related('category').order_by('-date', '-created_at')[:10]
        
        # Top spending categories (top 5)
        top_categories = categories_data[:5] if categories_data else []
        
        # Calculate savings (budget - expenses)
        savings = remaining if remaining > 0 else Decimal('0.00')
        
        # Get user currency
        user_settings, _ = UserSettings.objects.get_or_create(user=user)
        currency = user_settings.currency
        
        return Response({
            'message': 'Dashboard summary retrieved successfully',
            'data': {
                'month': current_month.strftime('%Y-%m'),
                'month_name': current_month.strftime('%B %Y'),
                'currency': currency,
                'summary': {
                    'total_budget': float(total_budget),
                    'total_expenses': float(total_expenses),
                    'remaining_budget': float(remaining),
                    'savings': float(savings),
                    'utilization_percent': utilization_percent,
                    'expense_count': expenses.count(),
                    'budget_status': 'over_budget' if total_expenses > total_budget else 'on_track'
                },
                'categories': categories_data,
                'top_spending_categories': top_categories,
                'recent_expenses': ExpenseSerializer(recent_expenses, many=True).data
            }
        })
        
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Failed to retrieve dashboard summary'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== SPENDING TRENDS API ====================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def spending_trends(request):
    """
    Get spending trends over time for charts.
    
    Query Parameters:
    - period: 'weekly', 'monthly', 'yearly' (default: monthly)
    - months: number of months to include (default: 6)
    """
    try:
        user = request.user
        period = request.GET.get('period', 'monthly')
        months = int(request.GET.get('months', 6))
        
        if months < 1 or months > 24:
            months = 6
        
        today = timezone.now().date()
        
        if period == 'monthly':
            # Get last N months data
            trends_data = []
            
            for i in range(months - 1, -1, -1):
                month_date = today - relativedelta(months=i)
                month_start = month_date.replace(day=1)
                
                # Get expenses for this month
                month_expenses = Expense.objects.filter(
                    user=user,
                    date__year=month_start.year,
                    date__month=month_start.month
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                
                # Get budget for this month
                month_budget = Budget.objects.filter(
                    user=user,
                    month=month_start
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                
                trends_data.append({
                    'period': month_start.strftime('%b %Y'),
                    'month': month_start.strftime('%Y-%m'),
                    'expenses': float(month_expenses),
                    'budget': float(month_budget),
                    'difference': float(month_budget - month_expenses)
                })
            
            return Response({
                'message': 'Spending trends retrieved successfully',
                'period': 'monthly',
                'data': trends_data
            })
        
        elif period == 'weekly':
            # Get last 8 weeks data
            trends_data = []
            
            for i in range(7, -1, -1):
                week_start = today - timedelta(weeks=i)
                week_end = week_start + timedelta(days=6)
                
                week_expenses = Expense.objects.filter(
                    user=user,
                    date__gte=week_start,
                    date__lte=week_end
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                
                trends_data.append({
                    'period': f"Week {week_start.strftime('%d %b')}",
                    'week_start': week_start.isoformat(),
                    'week_end': week_end.isoformat(),
                    'expenses': float(week_expenses)
                })
            
            return Response({
                'message': 'Weekly spending trends retrieved successfully',
                'period': 'weekly',
                'data': trends_data
            })
        
        else:
            return Response({
                'error': 'Invalid period. Use: weekly, monthly',
                'message': 'Invalid parameter'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Failed to retrieve spending trends'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== CATEGORY BREAKDOWN API ====================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def category_breakdown(request):
    """
    Get expense breakdown by category for pie/donut charts.
    
    Query Parameters:
    - month: YYYY-MM format (default: current month)
    - include_budget: true/false (default: true)
    """
    try:
        user = request.user
        
        # Get month parameter
        month_param = request.GET.get('month', '')
        if month_param:
            try:
                target_month = datetime.strptime(month_param, '%Y-%m').date().replace(day=1)
            except ValueError:
                return Response({
                    'error': 'Invalid month format. Use YYYY-MM',
                    'message': 'Invalid parameter'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            target_month = timezone.now().date().replace(day=1)
        
        include_budget = request.GET.get('include_budget', 'true').lower() == 'true'
        
        # Get all categories for this user
        categories = BudgetCategory.objects.filter(user=user)
        
        breakdown_data = []
        total_spent = Decimal('0.00')
        
        for category in categories:
            # Get expenses for this category in target month
            spent = Expense.objects.filter(
                user=user,
                category=category,
                date__year=target_month.year,
                date__month=target_month.month
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            total_spent += spent
            
            category_data = {
                'category_id': category.id,
                'category_name': category.name,
                'amount': float(spent)
            }
            
            if include_budget:
                # Get budget for this category
                budget = Budget.objects.filter(
                    user=user,
                    category=category,
                    month=target_month
                ).first()
                
                category_data['budget'] = float(budget.amount) if budget else 0.00
                category_data['budget_percent'] = round(
                    (spent / budget.amount) * 100, 2
                ) if budget and budget.amount > 0 else 0
            
            if spent > 0:  # Only include categories with expenses
                breakdown_data.append(category_data)
        
        # Calculate percentages
        for item in breakdown_data:
            item['percentage'] = round(
                (Decimal(item['amount']) / total_spent) * 100, 2
            ) if total_spent > 0 else 0
        
        # Sort by amount (highest first)
        breakdown_data.sort(key=lambda x: x['amount'], reverse=True)
        
        return Response({
            'message': 'Category breakdown retrieved successfully',
            'month': target_month.strftime('%Y-%m'),
            'total_spent': float(total_spent),
            'data': breakdown_data
        })
        
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Failed to retrieve category breakdown'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== BUDGET ADHERENCE API ====================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def budget_adherence(request):
    """
    Calculate budget adherence score and insights.
    Returns overall score and category-wise performance.
    """
    try:
        user = request.user
        current_month = timezone.now().date().replace(day=1)
        
        # Get budgets for current month
        budgets = Budget.objects.filter(
            user=user,
            month=current_month
        ).select_related('category')
        
        if not budgets.exists():
            return Response({
                'message': 'No budgets found for current month',
                'data': {
                    'score': 0,
                    'categories': []
                }
            })
        
        total_score = 0
        category_scores = []
        
        for budget in budgets:
            # Get expenses for this category
            spent = Expense.objects.filter(
                user=user,
                category=budget.category,
                date__year=current_month.year,
                date__month=current_month.month
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            # Calculate adherence score (100 = perfect, 0 = worst)
            if spent == 0:
                score = 100  # No spending is good
            elif spent <= budget.amount:
                # Proportional score: closer to budget = higher score
                score = int(100 - ((spent / budget.amount) * 50))
            else:
                # Over budget: penalty based on how much over
                over_percent = ((spent - budget.amount) / budget.amount) * 100
                score = max(0, int(50 - over_percent))
            
            total_score += score
            
            category_scores.append({
                'category': budget.category.name,
                'budget': float(budget.amount),
                'spent': float(spent),
                'score': score,
                'status': 'excellent' if score >= 80 else 'good' if score >= 60 else 'warning' if score >= 40 else 'critical'
            })
        
        # Overall score
        overall_score = int(total_score / budgets.count()) if budgets.count() > 0 else 0
        
        # Grade calculation
        if overall_score >= 90:
            grade = 'A+'
        elif overall_score >= 80:
            grade = 'A'
        elif overall_score >= 70:
            grade = 'B'
        elif overall_score >= 60:
            grade = 'C'
        else:
            grade = 'D'
        
        return Response({
            'message': 'Budget adherence calculated successfully',
            'data': {
                'overall_score': overall_score,
                'grade': grade,
                'categories': category_scores,
                'insights': {
                    'excellent_count': len([c for c in category_scores if c['score'] >= 80]),
                    'warning_count': len([c for c in category_scores if 40 <= c['score'] < 60]),
                    'critical_count': len([c for c in category_scores if c['score'] < 40])
                }
            }
        })
        
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Failed to calculate budget adherence'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== MONTH COMPARISON API ====================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def month_comparison(request):
    """
    Compare current month with previous month.
    Returns spending differences and insights.
    """
    try:
        user = request.user
        
        current_month = timezone.now().date().replace(day=1)
        previous_month = current_month - relativedelta(months=1)
        
        # Current month data
        current_expenses = Expense.objects.filter(
            user=user,
            date__year=current_month.year,
            date__month=current_month.month
        )
        
        current_total = current_expenses.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        # Previous month data
        previous_expenses = Expense.objects.filter(
            user=user,
            date__year=previous_month.year,
            date__month=previous_month.month
        )
        
        previous_total = previous_expenses.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        # Calculate difference
        difference = current_total - previous_total
        percent_change = round(
            (difference / previous_total) * 100, 2
        ) if previous_total > 0 else 0
        
        # Category-wise comparison
        categories = BudgetCategory.objects.filter(user=user)
        category_comparison = []
        
        for category in categories:
            current_cat = current_expenses.filter(
                category=category
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            previous_cat = previous_expenses.filter(
                category=category
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            cat_diff = current_cat - previous_cat
            cat_percent = round(
                (cat_diff / previous_cat) * 100, 2
            ) if previous_cat > 0 else 0
            
            if current_cat > 0 or previous_cat > 0:
                category_comparison.append({
                    'category': category.name,
                    'current_month': float(current_cat),
                    'previous_month': float(previous_cat),
                    'difference': float(cat_diff),
                    'percent_change': cat_percent,
                    'trend': 'up' if cat_diff > 0 else 'down' if cat_diff < 0 else 'same'
                })
        
        return Response({
            'message': 'Month comparison retrieved successfully',
            'data': {
                'current_month': {
                    'period': current_month.strftime('%B %Y'),
                    'total': float(current_total),
                    'expense_count': current_expenses.count()
                },
                'previous_month': {
                    'period': previous_month.strftime('%B %Y'),
                    'total': float(previous_total),
                    'expense_count': previous_expenses.count()
                },
                'comparison': {
                    'difference': float(difference),
                    'percent_change': percent_change,
                    'trend': 'increased' if difference > 0 else 'decreased' if difference < 0 else 'same',
                    'status': 'warning' if difference > 0 else 'good'
                },
                'category_comparison': category_comparison
            }
        })
        
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Failed to retrieve month comparison'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== EXPENSE STATISTICS API ====================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def expense_statistics(request):
    """
    Get detailed expense statistics.
    Returns: average, max, min, total count, etc.
    """
    try:
        user = request.user
        current_month = timezone.now().date().replace(day=1)
        
        # Current month expenses
        expenses = Expense.objects.filter(
            user=user,
            date__year=current_month.year,
            date__month=current_month.month
        )
        
        if not expenses.exists():
            return Response({
                'message': 'No expenses found for current month',
                'data': {
                    'total': 0,
                    'count': 0,
                    'average': 0,
                    'max': 0,
                    'min': 0
                }
            })
        
        stats = expenses.aggregate(
            total=Sum('amount'),
            count=Count('id'),
            average=Avg('amount'),
            max_amount=Max('amount'),
            min_amount=Min('amount')
        )
        
        # Get most expensive category
        category_totals = expenses.values('category__name').annotate(
            total=Sum('amount')
        ).order_by('-total')
        
        most_expensive_category = category_totals[0] if category_totals else None
        
        # Get transaction frequency
        total_days = (timezone.now().date() - current_month).days + 1
        avg_per_day = stats['total'] / total_days if total_days > 0 else Decimal('0.00')
        
        return Response({
            'message': 'Expense statistics retrieved successfully',
            'data': {
                'total': float(stats['total'] or 0),
                'count': stats['count'],
                'average': round(float(stats['average'] or 0), 2),
                'max': float(stats['max_amount'] or 0),
                'min': float(stats['min_amount'] or 0),
                'average_per_day': round(float(avg_per_day), 2),
                'most_expensive_category': {
                    'name': most_expensive_category['category__name'],
                    'total': float(most_expensive_category['total'])
                } if most_expensive_category else None
            }
        })
        
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Failed to retrieve expense statistics'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)