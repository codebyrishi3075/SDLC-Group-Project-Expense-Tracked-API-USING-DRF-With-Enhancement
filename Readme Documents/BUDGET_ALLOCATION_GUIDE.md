# Budget Allocation & Currency Settings Guide

## 📋 Overview

This document explains how budget allocation works in the Expense Tracker application, specifically addressing the distinction between:
1. **Monthly Budget Limit** (global user setting)
2. **Category Budgets** (allocated per category per month)
3. **Currency Settings** (user's preferred currency)

---

## 💰 Currency Settings

### What is Currency Setting?

Currency is a **user-level preference** that defines which currency the user operates in. This is stored in the `UserSettings` model and applies globally to all transactions.

### Supported Currencies

Currently supported ISO 4217 currency codes:
- `USD` - US Dollar
- `EUR` - Euro
- `INR` - Indian Rupee (default)
- `GBP` - British Pound
- `JPY` - Japanese Yen
- `AUD` - Australian Dollar
- `CAD` - Canadian Dollar

*(More can be added to the `CURRENCY_CHOICES` list in `usersettings/models.py`)*

### API Endpoints for Currency

#### 1. Get All Available Currency Options
```
GET /api/usersettings/currencies/
```

**Response:**
```json
{
  "message": "Currency options retrieved",
  "data": [
    {"code": "USD", "label": "US Dollar"},
    {"code": "EUR", "label": "Euro"},
    {"code": "INR", "label": "Indian Rupee"},
    ...
  ],
  "count": 8
}
```

#### 2. Get User's Current Settings (including currency)
```
GET /api/usersettings/
```
**Requires:** Authentication (Bearer token)

**Response:**
```json
{
  "message": "User settings retrieved successfully",
  "data": {
    "currency": "INR",
    "monthly_budget_limit": 50000.00
  }
}
```

#### 3. Update User's Currency Setting
```
PUT /api/usersettings/update/
```
**Requires:** Authentication (Bearer token)

**Request Body:**
```json
{
  "currency": "USD"
}
```

**Response:**
```json
{
  "message": "User settings updated successfully",
  "data": {
    "currency": "USD",
    "monthly_budget_limit": 50000.00
  }
}
```

---

## 📊 Budget Allocation Logic

### Key Concepts

| Term | Definition | Scope |
|------|-----------|-------|
| **Monthly Budget Limit** | Optional global cap on total spending per month | User-level setting |
| **Category Budget** | Allocated amount for a specific category in a specific month | Category + Month |
| **Actual Spending** | Sum of all expenses for a category in that month | Expenses per category per month |
| **Utilization** | (Actual Spending / Category Budget) × 100 | Percentage indicator |

### Important: Budget is MONTHLY

**Each `Budget` is allocated for a specific month**, not all-time.

**Model Structure:**
```python
class Budget(models.Model):
    user = ForeignKey(User)
    category = ForeignKey(BudgetCategory)
    month = DateField()          # First day of month (e.g., 2026-02-01)
    amount = DecimalField()      # Budget for this category this month
```

The **unique constraint** is: `(user, category, month)` — meaning **one budget per category per month**.

---

## 🎯 Example: User Scenario

### Your Example

```
User Settings:
  - Monthly Budget Limit: 5,000 INR (optional cap)
  
February 2026 - Category Budgets:
  1. Travel:            2,000 INR
  2. Grocery:           1,500 INR
  3. Entertainment:     1,000 INR
  4. Food & Dining:     1,500 INR
  5. Gifts & Donation:  2,000 INR
  ────────────────────────────────
  TOTAL:                8,000 INR ← Exceeds user's monthly limit of 5,000!
```

### What Happens?

#### ✅ The System **ALLOWS** Overallocation

The allocation is **NOT prevented** automatically. Here's why:

1. **`monthly_budget_limit` is optional** (`null=True, blank=True`)
2. **No validation enforces**that category budgets ≤ monthly limit
3. **System provides feedback** via the **Budget Utilization endpoint**

#### 📈 How Budget Utilization Works

**Endpoint:** `GET /api/budgets/budgets/utilization/?month=2026-02`

**Response for your scenario:**
```json
{
  "message": "Budget utilization ...",
  "month": "2026-02",
  "data": [
    {
      "category_name": "Gifts & Donation",
      "budget": 2000.00,
      "spent": 0.00,
      "remaining": 2000.00,
      "utilization_percent": 0.0,
      "status": "good"
    },
    {
      "category_name": "Travel",
      "budget": 2000.00,
      "spent": 1500.00,
      "remaining": 500.00,
      "utilization_percent": 75.0,
      "status": "warning"    ← User is at 75%
    },
    ...
  ],
  "summary": {
    "total_budget": 8000.00,
    "total_spent": 3500.00,
    "total_remaining": 4500.00,
    "overall_utilization_percent": 43.75,
    "warning_count": 2,
    "critical_count": 0,
    "over_budget_count": 0
  },
  "compliance": {
    "total_budget_exceeds_limit": true,
    "message": "Combined category budgets (8000.00) exceed monthly limit (5000.00) by 3000.00"
  }
}
```

### Status Levels

- `good` — Utilization < 75%
- `warning` — Utilization 75–89%
- `critical` — Utilization 90–99%
- `over_budget` — Utilization ≥ 100%

---

## 🔧 Recommended Addition: Validation

To **enforce** that category budgets don't exceed the user's monthly limit, add this validator:

**File: `api_budgets/views.py` in `create_budget()` function**

```python
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
        
        # ✅ ADD THIS: Check total category budgets against monthly limit
        new_amount = serializer.validated_data['amount']
        user_settings = request.user.settings  # OneToOne relation
        
        if user_settings.monthly_budget_limit:
            # Sum all budgets for this user in this month
            existing_total = Budget.objects.filter(
                user=request.user,
                month=month
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            new_total = existing_total + new_amount
            
            if new_total > user_settings.monthly_budget_limit:
                return Response({
                    'error': f'Total budgets ({new_total}) exceed your monthly limit ({user_settings.monthly_budget_limit})',
                    'message': 'Budget exceeds monthly limit',
                    'details': {
                        'existing_total': float(existing_total),
                        'new_budget': float(new_amount),
                        'new_total': float(new_total),
                        'monthly_limit': float(user_settings.monthly_budget_limit),
                        'exceeds_by': float(new_total - user_settings.monthly_budget_limit)
                    }
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
```

---

## 📅 Budget is Created Per Month

Each time a user wants to allocate budgets, they do so **for a specific month**.

### Example Timeline

**January 2026:**
```
Travel:        2,000
Grocery:       1,500
Entertainment: 1,000
```

**February 2026:** *(New budgets for new month)*
```
Travel:        2,200  ← Can change the amount
Grocery:       1,200  ← Or skip categories entirely
Entertainment: 1,100
```

**Database Behavior:**
- Creates separate `Budget` records for each (user, category, month) combination
- January budgets are independent from February budgets
- Past budgets are not automatically rolled forward

---

## 🚀 Recommended API Endpoints Summary

### Currency Settings
1. ✅ `GET /api/usersettings/currencies/` — List all currencies (public)
2. ✅ `GET /api/usersettings/` — Get user's current settings (auth required)
3. ✅ `PUT /api/usersettings/update/` — Update currency & monthly limit (auth required)

### Budget Management
4. ✅ `POST /api/budgets/create/` — Create a category
5. ✅ `GET /api/budgets/` — List categories
6. ✅ `PUT /api/budgets/update/<id>/` — Update category
7. ✅ `DELETE /api/budgets/delete/<id>/` — Delete category

8. ✅ `POST /api/budgets/budgets/create/` — Create budget for month (with optional validation)
9. ✅ `GET /api/budgets/budgets/` — List budgets (with filtering by month)
10. ✅ `PUT /api/budgets/budgets/<id>/update/` — Update budget amount
11. ✅ `DELETE /api/budgets/budgets/<id>/delete/` — Delete budget
12. ✅ `GET /api/budgets/budgets/utilization/` — Check spending vs budget for month

---

## ⚠️ Current Behavior vs. Recommended

| Aspect | Current | Recommended |
|--------|---------|-------------|
| **Budget Overallocation** | Allowed (no validation) | Reject if exceeds monthly limit |
| **Monthly Limit** | Optional | Should be required or set to a default |
| **Feedback** | Utilization endpoint shows status | Add validation to prevent overspend upfront |
| **UI/UX** | Frontend should warn user | API should enforce business rule |

---

## 📝 Testing the Currency Feature

Run the test suite:
```bash
python manage.py test account
```

Tests now include:
- Currency options endpoint ✅
- Update user currency ✅
- Budget creation with category ✅
- Budget utilization checking ✅

---

## 🎓 Key Takeaways

1. **Currency** is a user-level setting (one per user)
2. **Budgets are monthly** — each month gets its own allocation
3. **No automatic prevention** of overallocation (currently) — use the utilization endpoint to check
4. **Validation can be added** to enforce monthly limits at the API level
5. **All amounts are in the user's selected currency**

---

## Next Steps

1. ✅ Test the new currency endpoints
2. Review the budget validation logic and decide: enforce or warn?
3. Update frontend to show currency selector and budget warnings
4. Document in your API documentation (Postman collection)

