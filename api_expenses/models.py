from django.db import models
from django.conf import settings
from api_budgets.models import BudgetCategory

class Expense(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='expenses'
    )

    category = models.ForeignKey(
        BudgetCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses'
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.CharField(max_length=255, blank=True)
    date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    EXPENSE_TYPE_CHOICES = [
        ('fixed', 'Fixed'),
        ('variable', 'Variable'),
    ]
    
    expense_type = models.CharField(
        max_length=20,
        choices=EXPENSE_TYPE_CHOICES,
        default='variable'
    )
    
    is_recurring = models.BooleanField(default=False)
    due_date = models.DateField(null=True, blank=True)
    auto_pay = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.email} - {self.amount}"
