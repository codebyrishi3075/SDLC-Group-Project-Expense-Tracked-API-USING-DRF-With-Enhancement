"""
Budget API Views - Complete Implementation
Includes: Categories CRUD + Monthly Budgets CRUD + Utilization
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime
from decimal import Decimal

from .models import BudgetCategory, Budget
from .serializers import BudgetCategorySerializer, BudgetSerializer
from api_expenses.models import Expense


# ==================== BUDGET CATEGORY ENDPOINTS ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_categories(request):
    """List all budget categories for the authenticated user."""
    try:
        categories = BudgetCategory.objects.filter(user=request.user).order_by('name')
        serializer = BudgetCategorySerializer(categories, many=True)
        
        return Response({
            'message': 'Categories retrieved successfully',
            'count': categories.count(),
            'data': serializer.data
        })
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Failed to retrieve categories'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_category(request):
    """Create a new budget category."""
    try:
        serializer = BudgetCategorySerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'error': serializer.errors,
                'message': 'Validation failed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if category already exists for this user
        name = serializer.validated_data['name']
        if BudgetCategory.objects.filter(user=request.user, name__iexact=name).exists():
            return Response({
                'error': 'A category with this name already exists',
                'message': 'Duplicate category'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        category = serializer.save(user=request.user)
        
        return Response({
            'message': 'Category created successfully',
            'data': BudgetCategorySerializer(category).data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Failed to create category'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_category(request, pk):
    """Update an existing budget category."""
    try:
        category = BudgetCategory.objects.filter(
            pk=pk,
            user=request.user
        ).first()
        
        if not category:
            return Response({
                'error': 'Category not found or you do not have permission',
                'message': 'Category not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = BudgetCategorySerializer(
            category,
            data=request.data,
            partial=True
        )
        
        if not serializer.is_valid():
            return Response({
                'error': serializer.errors,
                'message': 'Validation failed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check for duplicate name (excluding current category)
        if 'name' in request.data:
            name = serializer.validated_data['name']
            if BudgetCategory.objects.filter(
                user=request.user,
                name__iexact=name
            ).exclude(pk=pk).exists():
                return Response({
                    'error': 'A category with this name already exists',
                    'message': 'Duplicate category'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        
        return Response({
            'message': 'Category updated successfully',
            'data': serializer.data
        })
        
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Failed to update category'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_category(request, pk):
    """Delete a budget category."""
    try:
        category = BudgetCategory.objects.filter(
            pk=pk,
            user=request.user
        ).first()
        
        if not category:
            return Response({
                'error': 'Category not found or you do not have permission',
                'message': 'Category not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if category has budgets or expenses
        has_budgets = Budget.objects.filter(category=category).exists()
        has_expenses = Expense.objects.filter(category=category).exists()
        
        if has_budgets or has_expenses:
            return Response({
                'error': 'Cannot delete category with existing budgets or expenses',
                'message': 'Category in use',
                'details': {
                    'has_budgets': has_budgets,
                    'has_expenses': has_expenses
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        category.delete()
        
        return Response({
            'message': 'Category deleted successfully'
        })
        
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Failed to delete category'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== MONTHLY BUDGET ENDPOINTS ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_budgets(request):
    """
    List all budgets for the authenticated user.
    
    Query Parameters:
    - month: YYYY-MM format (filter by specific month)
    - category: category ID (filter by category)
    """
    try:
        budgets_qs = Budget.objects.filter(user=request.user).select_related('category')
        
        # Filter by month
        month_param = request.GET.get('month', '').strip()
        if month_param:
            try:
                month_date = datetime.strptime(month_param, '%Y-%m').date().replace(day=1)
                budgets_qs = budgets_qs.filter(month=month_date)
            except ValueError:
                return Response({
                    'error': 'Invalid month format. Use YYYY-MM',
                    'message': 'Invalid parameter'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Filter by category
        category_id = request.GET.get('category', '').strip()
        if category_id:
            try:
                category_id = int(category_id)
                budgets_qs = budgets_qs.filter(category_id=category_id)
            except ValueError:
                return Response({
                    'error': 'Category ID must be a valid integer',
                    'message': 'Invalid parameter'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        budgets = budgets_qs.order_by('-month', 'category__name')
        serializer = BudgetSerializer(budgets, many=True)
        
        # Calculate total budget
        total_budget = budgets.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        return Response({
            'message': 'Budgets retrieved successfully',
            'count': budgets.count(),
            'total_budget': float(total_budget),
            'data': serializer.data
        })
        
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Failed to retrieve budgets'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_budget(request):
    """Create a new monthly budget for a category."""
    try:
        serializer = BudgetSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'error': serializer.errors,
                'message': 'Validation failed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify category belongs to user
        category_id = request.data.get('category')
        if not BudgetCategory.objects.filter(id=category_id, user=request.user).exists():
            return Response({
                'error': 'Category not found or does not belong to you',
                'message': 'Invalid category'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check for duplicate budget (same user, category, month)
        month = serializer.validated_data['month']
        category = serializer.validated_data['category']
        
        if Budget.objects.filter(
            user=request.user,
            category=category,
            month=month
        ).exists():
            return Response({
                'error': 'Budget already exists for this category and month',
                'message': 'Duplicate budget'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        budget = serializer.save(user=request.user)
        
        return Response({
            'message': 'Budget created successfully',
            'data': BudgetSerializer(budget).data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Failed to create budget'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_budget(request, pk):
    """Update an existing budget."""
    try:
        budget = Budget.objects.filter(
            pk=pk,
            user=request.user
        ).first()
        
        if not budget:
            return Response({
                'error': 'Budget not found or you do not have permission',
                'message': 'Budget not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = BudgetSerializer(
            budget,
            data=request.data,
            partial=True
        )
        
        if not serializer.is_valid():
            return Response({
                'error': serializer.errors,
                'message': 'Validation failed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # If changing category, verify it belongs to user
        if 'category' in request.data:
            category_id = request.data.get('category')
            if not BudgetCategory.objects.filter(id=category_id, user=request.user).exists():
                return Response({
                    'error': 'Category not found or does not belong to you',
                    'message': 'Invalid category'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        
        return Response({
            'message': 'Budget updated successfully',
            'data': serializer.data
        })
        
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Failed to update budget'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_budget(request, pk):
    """Delete a budget."""
    try:
        budget = Budget.objects.filter(
            pk=pk,
            user=request.user
        ).first()
        
        if not budget:
            return Response({
                'error': 'Budget not found or you do not have permission',
                'message': 'Budget not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        budget.delete()
        
        return Response({
            'message': 'Budget deleted successfully'
        })
        
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Failed to delete budget'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== BUDGET UTILIZATION ENDPOINT ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def budget_utilization(request):
    """
    Get budget utilization for current or specified month.
    Shows budget vs actual spending for each category.
    
    Query Parameters:
    - month: YYYY-MM format (default: current month)
    """
    try:
        user = request.user
        
        # Get month parameter
        month_param = request.GET.get('month', '').strip()
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
        
        # Get budgets for the month
        budgets = Budget.objects.filter(
            user=user,
            month=target_month
        ).select_related('category')
        
        if not budgets.exists():
            return Response({
                'message': 'No budgets found for this month',
                'month': target_month.strftime('%Y-%m'),
                'data': []
            })
        
        utilization_data = []
        total_budget = Decimal('0.00')
        total_spent = Decimal('0.00')
        
        for budget in budgets:
            # Get expenses for this category in target month
            expenses = Expense.objects.filter(
                user=user,
                category=budget.category,
                date__year=target_month.year,
                date__month=target_month.month
            )
            
            spent = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            remaining = budget.amount - spent
            utilization_percent = round(
                (spent / budget.amount) * 100, 2
            ) if budget.amount > 0 else 0
            
            total_budget += budget.amount
            total_spent += spent
            
            # Determine status
            if utilization_percent >= 100:
                status_text = 'over_budget'
            elif utilization_percent >= 90:
                status_text = 'critical'
            elif utilization_percent >= 75:
                status_text = 'warning'
            else:
                status_text = 'good'
            
            utilization_data.append({
                'category_id': budget.category.id,
                'category_name': budget.category.name,
                'budget': float(budget.amount),
                'spent': float(spent),
                'remaining': float(remaining),
                'utilization_percent': utilization_percent,
                'status': status_text,
                'expense_count': expenses.count()
            })
        
        # Sort by utilization percentage (highest first)
        utilization_data.sort(key=lambda x: x['utilization_percent'], reverse=True)
        
        # Overall summary
        overall_utilization = round(
            (total_spent / total_budget) * 100, 2
        ) if total_budget > 0 else 0
        
        return Response({
            'message': 'Budget utilization retrieved successfully',
            'month': target_month.strftime('%Y-%m'),
            'month_name': target_month.strftime('%B %Y'),
            'summary': {
                'total_budget': float(total_budget),
                'total_spent': float(total_spent),
                'total_remaining': float(total_budget - total_spent),
                'overall_utilization': overall_utilization,
                'categories_count': len(utilization_data),
                'over_budget_count': len([d for d in utilization_data if d['status'] == 'over_budget']),
                'critical_count': len([d for d in utilization_data if d['status'] == 'critical'])
            },
            'data': utilization_data
        })
        
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Failed to retrieve budget utilization'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)