from django.urls import path
from .views import ContactUsAPIView

urlpatterns = [
    path('submit/', ContactUsAPIView.as_view(), name='contact-submit'),
]

# localhost:8000/api/contact/submit/ -> POST with JSON body:
# {
#     "full_name": "John Doe",
#     "email": "
#     "subject": "Inquiry about services",
#     "message": "I would like to know more about your services."
# }