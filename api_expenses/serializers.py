from rest_framework import serializers
from .models import Expense
from datetime import datetime, date
from decimal import Decimal


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = [
            'id',
            'amount',
            'category',
            'notes',
            'date',
            'expense_type',
            'is_recurring',
            'due_date',
            'auto_pay',
            'created_at',
        ]

    def validate_amount(self, value):
        """Validate that amount is positive and within reasonable limits."""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        if value > Decimal('9999999.99'):
            raise serializers.ValidationError("Amount exceeds maximum allowed value.")
        return value

    def validate_date(self, value):
        """Validate that date is not in the future."""
        if isinstance(value, str):
            value = datetime.strptime(value, '%Y-%m-%d').date()
        if value > date.today():
            raise serializers.ValidationError("Expense date cannot be in the future.")
        return value

    def validate_category(self, value):
        """Validate that category exists and belongs to the user."""
        if not value:
            raise serializers.ValidationError("Category is required.")
        return value

    def validate_notes(self, value):
        """Validate notes field length."""
        if value and len(value) > 255:
            raise serializers.ValidationError("Notes cannot exceed 255 characters.")
        return value
