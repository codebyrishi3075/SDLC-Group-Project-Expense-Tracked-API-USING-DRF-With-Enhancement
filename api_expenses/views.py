from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import IntegrityError
from datetime import datetime, date
from django.http import HttpResponse, request
from decimal import InvalidOperation, Decimal
from .models import Expense
from .serializers import ExpenseSerializer
from django.db.models import Q


from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO

# ------------------Export Expenses as PDF (user-scoped)---------------------------
@api_view(['GET'])
def export_expenses_pdf(request):
    user = request.user

    from_param = request.GET.get('from')
    to_param = request.GET.get('to')

    if from_param and to_param:
        start_date = date.fromisoformat(from_param)
        end_date = date.fromisoformat(to_param)
    else:
        today = date.today()
        start_date = date(today.year, today.month, 1)
        end_date = today

    expenses = Expense.objects.filter(
        user=user,
        date__range=[start_date, end_date]
    ).select_related('category')

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 50
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, f"Expense Report ({start_date} to {end_date})")

    y -= 30
    p.setFont("Helvetica", 10)

    for exp in expenses:
        if y < 50:
            p.showPage()
            y = height - 50

        line = f"{exp.date} | {exp.category.name if exp.category else 'Uncategorized'} | ₹{exp.amount} | {exp.notes}"
        p.drawString(50, y, line)
        y -= 15

    p.showPage()
    p.save()

    buffer.seek(0)

    response = HttpResponse(
        buffer,
        content_type='application/pdf'
    )
    response['Content-Disposition'] = (
        f'attachment; filename="expenses_{start_date}_to_{end_date}.pdf"'
    )

    return response


def paginate_results(queryset, page_number, page_size=10):
    """Helper function to handle pagination with error handling."""
    try:
        paginator = Paginator(queryset, page_size)
        page = paginator.get_page(page_number)
        return page, paginator, None
    except (PageNotAnInteger, EmptyPage) as e:
        return None, None, f"Invalid page number: {str(e)}"


# ------------------Create Expenses (user-scoped with pagination)---------------------------
@api_view(['POST'])
def create_expense(request):
    """Create a new expense with validated input."""
    try:
        if not request.data:
            return Response({
                'error': 'Request body is required',
                'message': 'Failed to create expense'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = ExpenseSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'error': serializer.errors,
                'message': 'Validation failed'
            }, status=status.HTTP_400_BAD_REQUEST)

        expense = serializer.save(user=request.user)

        return Response({
            'message': 'Expense created successfully',
            'data': ExpenseSerializer(expense).data
        }, status=status.HTTP_201_CREATED)
    
    except IntegrityError as e:
        return Response({
            'error': 'A database constraint was violated',
            'message': 'Failed to create expense'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Failed to create expense'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# ----------------------Updated Expenses with Search (user-scoped with pagination)-----------------------
@api_view(['GET'])
def list_expenses(request):
    """List all expenses with filtering, search, and pagination."""
    try:
        user = request.user
        expenses_qs = Expense.objects.filter(user=user)

        # 🔍 Enhanced Search (multiple fields)
        search = request.GET.get('search', '').strip()
        if search:
            if len(search) > 255:
                return Response({
                    'error': 'Search query is too long (max 255 characters)',
                    'message': 'Invalid search parameter'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Search in both notes AND category name
            expenses_qs = expenses_qs.filter(
                Q(notes__icontains=search) | 
                Q(category__name__icontains=search)
            )

            # Build search query across multiple fields
            # search_query = Q(notes__icontains=search)
            # Search in category name if category relation exists
            # search_query |= Q(category__name__icontains=search)

            # Search by amount if it's a valid number
            try:
                amount_search = Decimal(search)
                search_query |= Q(amount=amount_search)
            except:
                pass  # Not a number, skip amount search
            
            expenses_qs = expenses_qs.filter(search_query)

        # 🗂 Filter by category
        category_id = request.GET.get('category', '').strip()
        if category_id:
            try:
                category_id = int(category_id)
                expenses_qs = expenses_qs.filter(category_id=category_id)
            except ValueError:
                return Response({
                    'error': 'Category ID must be a valid integer',
                    'message': 'Invalid category parameter'
                }, status=status.HTTP_400_BAD_REQUEST)
            

        # 💰 Amount range filter
        amount_min = request.GET.get('amount_min', '').strip()
        amount_max = request.GET.get('amount_max', '').strip()

        if amount_min or amount_max:
            try:
                if amount_min and amount_max:
                    min_val = Decimal(amount_min)
                    max_val = Decimal(amount_max)

                    if min_val < 0 or max_val < 0:
                        return Response({
                            'error': 'Amount values must be positive',
                            'message': 'Invalid amount range'
                        }, status=status.HTTP_400_BAD_REQUEST)

                    if min_val > max_val:
                        return Response({
                            'error': 'Minimum amount must be less than maximum',
                            'message': 'Invalid amount range'
                        }, status=status.HTTP_400_BAD_REQUEST)

                    expenses_qs = expenses_qs.filter(
                        amount__gte=min_val,
                        amount__lte=max_val
                    )
                elif amount_min:
                    expenses_qs = expenses_qs.filter(amount__gte=Decimal(amount_min))
                elif amount_max:
                    expenses_qs = expenses_qs.filter(amount__lte=Decimal(amount_max))

            except (ValueError, InvalidOperation):
                return Response({
                    'error': 'Invalid amount values',
                    'message': 'Invalid filter'
                }, status=status.HTTP_400_BAD_REQUEST)
    
        # 📅 Date range filter with validation
        from_date = request.GET.get('from', '').strip()
        to_date = request.GET.get('to', '').strip()

        if from_date or to_date:
            try:
                if not from_date:
                    return Response({
                        'error': 'Both "from" and "to" date parameters are required',
                        'message': 'Invalid date range'
                    }, status=status.HTTP_400_BAD_REQUEST)
                if not to_date:
                    return Response({
                        'error': 'Both "from" and "to" date parameters are required',
                        'message': 'Invalid date range'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                from_date_obj = datetime.strptime(from_date, "%Y-%m-%d").date()
                to_date_obj = datetime.strptime(to_date, "%Y-%m-%d").date()
                
                if from_date_obj > to_date_obj:
                    return Response({
                        'error': 'Start date must be before or equal to end date',
                        'message': 'Invalid date range'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                expenses_qs = expenses_qs.filter(date__range=[from_date_obj, to_date_obj])
            
            except ValueError as e:
                return Response({
                    'error': 'Invalid date format. Use YYYY-MM-DD format',
                    'message': 'Invalid date parameter'
                }, status=status.HTTP_400_BAD_REQUEST)

        # 🔄 Sorting
        sort_by = request.GET.get('sort_by', '-date')  # default: newest first
        allowed_sorts = ['date', '-date', 'amount', '-amount', 'created_at', '-created_at']

        if sort_by in allowed_sorts:
            expenses_qs = expenses_qs.order_by(sort_by)
        else:
            # Default sorting
            expenses_qs = expenses_qs.order_by('-date')

        # Handle empty queryset after all filters
        if not expenses_qs.exists():
            return Response({
                'message': 'No expenses found matching the criteria',
                'count': 0,
                'num_pages': 0,
                'current_page': 0,
                'data': []
            }, status=status.HTTP_200_OK)

        # 📄 Pagination with validation
        page_number = request.GET.get('page', 1)
        page_size_param = request.GET.get('page_size', 10)
        
        try:
            page_size = int(page_size_param)
            if page_size < 1 or page_size > 100:
                page_size = 10
        except ValueError:
            page_size = 10

        page, paginator, error = paginate_results(expenses_qs, page_number, page_size)
        
        if error:
            return Response({
                'error': error,
                'message': 'Pagination error'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = ExpenseSerializer(page, many=True)

        return Response({
            'message': 'Expenses retrieved successfully',
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page.number,
            'has_next': page.has_next(),
            'has_previous': page.has_previous(),
            'page_size': page_size,
            'data': serializer.data
        })
    
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Failed to retrieve expenses'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
# ------------------UPDATE Expense (own only)---------------------------
@api_view(['PUT'])
def update_expense(request, pk):
    """Update an expense with validation."""
    try:
        if not pk:
            return Response({
                'error': 'Expense ID is required',
                'message': 'Invalid request'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            pk = int(pk)
        except ValueError:
            return Response({
                'error': 'Expense ID must be a valid integer',
                'message': 'Invalid request'
            }, status=status.HTTP_400_BAD_REQUEST)

        expense = Expense.objects.filter(
            pk=pk,
            user=request.user
        ).first()

        if not expense:
            return Response({
                'error': 'Expense not found or you do not have permission to modify it',
                'message': 'Expense not found'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ExpenseSerializer(
            expense,
            data=request.data,
            partial=True
        )
        
        if not serializer.is_valid():
            return Response({
                'error': serializer.errors,
                'message': 'Validation failed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()

        return Response({
            'message': 'Expense updated successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Failed to update expense'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ------------------DELETE Expense (own only)---------------------------
@api_view(['DELETE'])
def delete_expense(request, pk):
    """Delete an expense with proper authorization."""
    try:
        if not pk:
            return Response({
                'error': 'Expense ID is required',
                'message': 'Invalid request'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            pk = int(pk)
        except ValueError:
            return Response({
                'error': 'Expense ID must be a valid integer',
                'message': 'Invalid request'
            }, status=status.HTTP_400_BAD_REQUEST)

        expense = Expense.objects.filter(
            pk=pk,
            user=request.user
        ).first()

        if not expense:
            return Response({
                'error': 'Expense not found or you do not have permission to delete it',
                'message': 'Expense not found'
            }, status=status.HTTP_404_NOT_FOUND)

        expense.delete()
        return Response({
            'message': 'Expense deleted successfully'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Failed to delete expense'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

