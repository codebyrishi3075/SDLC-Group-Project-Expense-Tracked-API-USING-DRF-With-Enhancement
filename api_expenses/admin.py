from django.contrib import admin
from .models import Expense

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'amount',
        'notes',
        'date',
        'created_at',
    )
    list_filter = ('date', 'notes')
    search_fields = ('user__email', 'notes')