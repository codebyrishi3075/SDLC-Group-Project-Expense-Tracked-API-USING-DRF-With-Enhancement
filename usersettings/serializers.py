from rest_framework import serializers
from .models import UserSettings

class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = [
            'currency',
            'monthly_budget_limit',
        ]
        read_only_fields = ['id', 'user']  # Assuming 'user' is a ForeignKey to the User model