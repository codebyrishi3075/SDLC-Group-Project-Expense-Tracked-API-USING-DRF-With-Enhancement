from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('verify-otp/', views.verify_email_otp, name='verify_otp'),
    path('login/', views.login_user, name='login'),
    path('profile/', views.profile, name='profile'),

    # -----User Profile Management-----
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/avatar/', views.upload_avatar, name='upload_avatar'),

    # --------Password reset URLs
    path('password-reset/request/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/verify-otp/', views.password_reset_verify_otp, name='password_reset_verify_otp'),
    path('password-reset/confirm/', views.password_reset_confirm, name='password_reset_confirm'),

]


