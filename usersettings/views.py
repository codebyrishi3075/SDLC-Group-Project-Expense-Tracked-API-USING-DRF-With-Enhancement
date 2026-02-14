from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import UserSettings
from . serializers import UserSettingsSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_settings(request):
    """Retrieve the authenticated user's settings."""
    try:
        settings_obj, created = UserSettings.objects.get_or_create(
            user=request.user
        )

        serializer = UserSettingsSerializer(settings_obj)
        return Response({
            'message': 'User settings retrieved successfully',
            'data': serializer.data
        })
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Failed to retrieve user settings'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_settings(request):
    """Update the authenticated user's settings (currency and/or monthly budget)."""
    try:
        settings_obj, _ = UserSettings.objects.get_or_create(
            user=request.user
        )

        serializer = UserSettingsSerializer(
            settings_obj,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'message': 'User settings updated successfully',
            'data': serializer.data
        })
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Failed to update settings'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_currency_options(request):
    """
    Get all available currency options for selection.
    Public endpoint - no authentication required.
    Returns list of (code, label) pairs.
    """
    try:
        currencies = [
            {
                'code': code,
                'label': label
            }
            for code, label in UserSettings.CURRENCY_CHOICES
        ]
        return Response({
            'message': 'Currency options retrieved',
            'data': currencies,
            'count': len(currencies)
        })
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Failed to retrieve currency options'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


