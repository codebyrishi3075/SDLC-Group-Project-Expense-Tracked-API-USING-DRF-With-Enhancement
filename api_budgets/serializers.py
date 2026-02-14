from rest_framework import serializers
from .models import BudgetCategory, Budget
from decimal import Decimal
from datetime import datetime, date


class BudgetCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetCategory
        fields = ['id', 'name']

    def validate_name(self, value):
        """Validate category name."""
        if not value or not value.strip():
            raise serializers.ValidationError("Category name cannot be empty.")
        if len(value) > 100:
            raise serializers.ValidationError("Category name cannot exceed 100 characters.")
        return value.strip()


class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = [
            'id',
            'category',
            'month',
            'amount',
        ]

    def validate_amount(self, value):
        """Validate that budget amount is positive and within reasonable limits."""
        if value <= 0:
            raise serializers.ValidationError("Budget amount must be greater than zero.")
        if value > Decimal('9999999.99'):
            raise serializers.ValidationError("Budget amount exceeds maximum allowed value.")
        return value

    def validate_month(self, value):
        """Validate that month is in valid format and not too far in the past."""
        if isinstance(value, str):
            try:
                value = datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                raise serializers.ValidationError("Month must be in YYYY-MM-DD format.")
        
        # Allow budgets for past 12 months and future 24 months
        today = date.today()
        month_date = date(value.year, value.month, 1)
        year_diff = (month_date.year - today.year) * 12 + (month_date.month - today.month)
        
        if year_diff < -12:
            raise serializers.ValidationError("Cannot create budgets for dates older than 12 months.")
        if year_diff > 24:
            raise serializers.ValidationError("Cannot create budgets more than 24 months in the future.")
        
        return value

    def validate_category(self, value):
        """Validate that category exists."""
        if not value:
            raise serializers.ValidationError("Category is required.")
        return value
