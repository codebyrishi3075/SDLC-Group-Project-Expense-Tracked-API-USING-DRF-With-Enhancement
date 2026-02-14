from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import ContactMessageSerializer
from .models import ContactMessage

class ContactUsAPIView(APIView):
    authentication_classes = []  # Public
    permission_classes = []

    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        contact = serializer.save(
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        # Optional: trigger email async later
        # send_contact_email(contact)

        return Response(
            {"message": "Your message has been sent successfully."},
            status=status.HTTP_201_CREATED
        )

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
