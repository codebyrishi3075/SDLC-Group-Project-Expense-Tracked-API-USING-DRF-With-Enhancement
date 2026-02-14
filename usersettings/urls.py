from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_user_settings),
    path('update/', views.update_user_settings),
    path('currencies/', views.get_currency_options),
]