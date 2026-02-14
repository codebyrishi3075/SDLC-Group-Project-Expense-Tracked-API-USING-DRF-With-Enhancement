# Currency Settings & Budget Allocation - Implementation Guide

## 📌 Quick Reference

### Currency Settings - New Endpoints

| Endpoint | Method | Auth? | Purpose |
|----------|--------|-------|---------|
| `/api/usersettings/currencies/` | GET | ❌ No | List all available currencies |
| `/api/usersettings/` | GET | ✅ Yes | Get user's currency & settings |
| `/api/usersettings/update/` | PUT | ✅ Yes | Change user's currency |

### Budget Allocation - Existing Endpoints

| Endpoint | Method | Auth? | Purpose |
|----------|--------|-------|---------|
| `/api/budgets/` | GET | ✅ Yes | List user's categories |
| `/api/budgets/create/` | POST | ✅ Yes | Create new category |
| `/api/budgets/budgets/create/` | POST | ✅ Yes | Create budget for month |
| `/api/budgets/budgets/` | GET | ✅ Yes | List budgets (filter by month) |
| `/api/budgets/budgets/utilization/` | GET | ✅ Yes | Check spending vs budget |

---

## 🌍 Step 1: Get Available Currencies

**Endpoint:** `GET /api/usersettings/currencies/`

**Authentication:** Not required (public endpoint)

**cURL Example:**
```bash
curl -X GET http://localhost:8000/api/usersettings/currencies/
```

**Response:**
```json
{
  "message": "Currency options retrieved",
  "data": [
    {
      "code": "USD",
      "label": "US Dollar"
    },
    {
      "code": "EUR",
      "label": "Euro"
    },
    {
      "code": "INR",
      "label": "Indian Rupee"
    },
    {
      "code": "GBP",
      "label": "British Pound"
    },
    {
      "code": "JPY",
      "label": "Japanese Yen"
    },
    {
      "code": "AUD",
      "label": "Australian Dollar"
    },
    {
      "code": "CAD",
      "label": "Canadian Dollar"
    }
  ],
  "count": 7
}
```

Use this to populate a **dropdown in your frontend**.

---

## 💾 Step 2: Set User's Currency

**Endpoint:** `PUT /api/usersettings/update/`

**Authentication:** Required (Bearer token)

**cURL Example:**
```bash
curl -X PUT http://localhost:8000/api/usersettings/update/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"currency": "USD"}'
```

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
    "monthly_budget_limit": null
  }
}
```

Once set, **all budgets and expenses are in the selected currency**.

---

## 💰 Step 3: Optionally Set Monthly Budget Limit

**Endpoint:** `PUT /api/usersettings/update/`

**Purpose:** Set an optional global cap on total monthly spending across all categories.

**Request:**
```json
{
  "currency": "USD",
  "monthly_budget_limit": 5000.00
}
```

**Response:**
```json
{
  "message": "User settings updated successfully",
  "data": {
    "currency": "USD",
    "monthly_budget_limit": 5000.00
  }
}
```

---

## 📊 Step 4: Allocate Budget for a Month

### Example Scenario

**User Settings:**
- Currency: `USD`
- Monthly Budget Limit: `5000` ← Global cap

**Create Categories First:**
```bash
# Create Travel category
curl -X POST http://localhost:8000/api/budgets/create/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Travel"}'

# Create Grocery category
curl -X POST http://localhost:8000/api/budgets/create/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Grocery"}'

# ... and so on for Entertainment, Food & Dining, Gifts & Donation
```

**Then Allocate Budgets for February 2026:**

```bash
# Allocate $2000 to Travel in Feb 2026
curl -X POST http://localhost:8000/api/budgets/budgets/create/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "category": 1,
    "amount": "2000.00",
    "month": "2026-02-01"
  }'

# Allocate $1500 to Grocery
curl -X POST http://localhost:8000/api/budgets/budgets/create/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "category": 2,
    "amount": "1500.00",
    "month": "2026-02-01"
  }'

# ... and so on
```

---

## ⚠️ Important: Budget Overallocation

Your scenario:
```
Monthly Limit:  5,000 USD
Allocated:      8,000 USD (across 5 categories)
```

### Current Behavior (No Validation)

The system **ALLOWS** this overallocation. No error is thrown.

### Why?

The `monthly_budget_limit` is **advisory**, not enforced. The system tracks it but doesn't prevent exceeding it.

### How to Know You're Over Budget?

Use the **Budget Utilization Endpoint** to see the status:

```bash
curl -X GET "http://localhost:8000/api/budgets/budgets/utilization/?month=2026-02" \
  -H "Authorization: Bearer TOKEN"
```

**Response:**
```json
{
  "message": "Budget utilization for 2026-02",
  "month": "2026-02",
  "data": [
    {
      "category_name": "Travel",
      "budget": 2000.00,
      "spent": 1500.00,
      "remaining": 500.00,
      "utilization_percent": 75.0,
      "status": "warning"  ← 75% of budget used
    },
    {
      "category_name": "Grocery",
      "budget": 1500.00,
      "spent": 200.00,
      "remaining": 1300.00,
      "utilization_percent": 13.3,
      "status": "good"
    }
  ],
  "summary": {
    "total_budget": 8000.00,
    "total_spent": 1700.00,
    "total_remaining": 6300.00,
    "overall_utilization_percent": 21.25,
    "warning_count": 1,
    "critical_count": 0,
    "over_budget_count": 0
  },
  "compliance": {
    "total_budget_exceeds_limit": true,
    "message": "Combined category budgets (8000.00) exceed monthly limit (5000.00) by 3000.00"
  }
}
```

### Key Fields

- **status** — `good` (0–74%), `warning` (75–89%), `critical` (90–99%), `over_budget` (≥100%)
- **compliance.message** — Warns if budgets exceed monthly limit
- **overall_utilization_percent** — Percentage of total budget spent

---

## 🔒 Recommended: Add Validation (Optional)

If you want to **prevent** overallocation, add validation to the budget creation endpoint. See [BUDGET_ALLOCATION_GUIDE.md](./BUDGET_ALLOCATION_GUIDE.md) for the code snippet to add.

---

## 🔄 Each Month is Independent

**Important:** Budgets are **monthly**, not cumulative across all time.

### Example

**January 2026:**
```
Total Allocated: 5000 USD
Total Spent:     3000 USD
```

**February 2026:** *(Fresh allocation)*
```
Total Allocated: 8000 USD  ← Can be different from January
Total Spent:     0 USD     ← Starts from zero
```

---

## 📱 Frontend Integration Example

### 1. Currency Selector (On Signup/Settings)

```javascript
// Fetch available currencies
fetch('/api/usersettings/currencies/')
  .then(res => res.json())
  .then(data => {
    // Populate <select> dropdown
    const select = document.getElementById('currency-select');
    data.data.forEach(curr => {
      const option = document.createElement('option');
      option.value = curr.code;
      option.textContent = curr.label;
      select.appendChild(option);
    });
  });

// When user selects a currency
document.getElementById('currency-select').addEventListener('change', (e) => {
  const token = localStorage.getItem('access_token');
  fetch('/api/usersettings/update/', {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      currency: e.target.value
    })
  })
  .then(res => res.json())
  .then(data => {
    console.log('Currency updated:', data.data.currency);
  });
});
```

### 2. Budget Allocation Form

```javascript
// When user allocates budgets for a month
async function allocateBudgets(month, categoryBudgets) {
  const token = localStorage.getItem('access_token');
  
  for (const [categoryId, amount] of Object.entries(categoryBudgets)) {
    const response = await fetch('/api/budgets/budgets/create/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        category: parseInt(categoryId),
        amount: parseFloat(amount),
        month: `${month}-01`  // Convert to YYYY-MM-DD format
      })
    });
    
    const data = await response.json();
    if (!response.ok) {
      console.error('Error creating budget:', data.error);
    }
  }
}

// Usage
allocateBudgets('2026-02', {
  1: 2000,    // Travel: 2000
  2: 1500,    // Grocery: 1500
  3: 1000,    // Entertainment: 1000
  4: 1500,    // Food & Dining: 1500
  5: 2000     // Gifts & Donation: 2000
});
```

### 3. Show Budget Status with Warnings

```javascript
// Fetch budget utilization
async function showBudgetStatus(month) {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(`/api/budgets/budgets/utilization/?month=${month}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  const data = await response.json();
  
  // Show warning if over monthly limit
  if (data.compliance.total_budget_exceeds_limit) {
    showWarning(`⚠️ Your allocated budgets (${data.summary.total_budget}) exceed your monthly limit (${data.compliance.message})`);
  }
  
  // Color-code categories by status
  data.data.forEach(cat => {
    const color = {
      'good': 'green',
      'warning': 'orange',
      'critical': 'red',
      'over_budget': 'darkred'
    }[cat.status];
    
    displayBudgetCard(cat, color);
  });
}

showBudgetStatus('2026-02');
```

---

## ✅ Best Practices

1. **Always fetch currencies** before letting user pick one
2. **Show the selected currency** in all forms and displays (e.g., "$2000" or "₹50000")
3. **Check utilization monthly** — don't let users spend blindly
4. **Consider setting a default monthly limit** — helps users plan better
5. **December/January handling** — Clearly separate budgets by month in UI
6. **Archive old budgets** — Optionally hide past months to reduce clutter

---

## 🧪 Test Your Integration

Run the test suite to confirm everything works:

```bash
python manage.py test account --verbosity=2
```

Expected output:
```
Ran 6 tests in 8.847s
OK
```

All 6 tests pass, including:
- ✅ Currency options endpoint
- ✅ Update currency
- ✅ Budget allocation
- ✅ Budget utilization
- ✅ Category management
- ✅ Expense tracking

---

## 📝 Summary of Your Question

> "Now User Allocate Amount For 5 Category - 8000 Now, You check the total allocated category amount is 8000 and initial budget for a month allocated 5000 they exceeded there budget so how its working or not?"

### Answer

1. **Budget is allocated PER MONTH** — Each month gets its own set of budgets
2. **System ALLOWS overallocation** — No validation prevents exceeding the monthly limit
3. **Feedback via Utilization endpoint** — Shows status: `good`, `warning`, `critical`, `over_budget`
4. **Optional validation** — Can be added to reject overallocation (see guide)
5. **Frontend should warn** — Use the compliance message to alert users

Your scenario (8000 allocated vs 5000 limit) would show `"total_budget_exceeds_limit": true` with a warning that they're over by 3000.

