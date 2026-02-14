import random
from django.core.mail import send_mail
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import EmailOTP, User
from .serializers import RegisterSerializer, ProfileSerializer


def generate_otp():
    return str(random.randint(100000, 999999))


# ---------------------------- REGISTER ----------------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    try:
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        otp = generate_otp()
        EmailOTP.objects.filter(user=user).delete()
        EmailOTP.objects.create(user=user, otp=otp)

        send_mail(
            subject='Verify your email',
            message=f'Your OTP is {otp}',
            from_email=None,
            recipient_list=[user.email],
        )

        return Response({
            'message': 'OTP sent successfully to email'
            },status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({
            'message': 'Failed to send OTP',
            'error': str(e)
            },status=status.HTTP_400_BAD_REQUEST)


# ----------------------------- VERIFY OTP ----------------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email_otp(request):
    try:
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email or not otp:
            return Response({'error': 'Email and OTP required'}, status=400)

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({'error': 'Invalid email'}, status=400)

        otp_obj = EmailOTP.objects.filter(
            user=user,
            otp=otp,
            is_used=False
        ).last()

        if not otp_obj:
            return Response({'error': 'Invalid OTP'}, status=400)

        if otp_obj.is_expired():
            return Response({'error': 'OTP expired'}, status=400)

        otp_obj.is_used = True
        otp_obj.save()

        user.is_active = True
        user.is_email_verified = True
        user.save()

        return Response({'message': 'Email verified successfully'})
    except Exception as e:
        return Response(
            {'error': str(e), 'message': 'Failed to verify OTP'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ------------------------------- LOGIN --------------------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    try:
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(username=email, password=password)

        if not user:
            return Response({'error': 'Invalid credentials'}, status=401)

        if not user.is_email_verified:
            return Response({'error': 'Email not verified'}, status=403)

        refresh = RefreshToken.for_user(user)

        return Response({
            'message': 'Login successful',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'email': user.email
            }
        })
    except Exception as e:
        return Response(
            {'error': str(e), 'message': 'Failed to login'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ------------------------------- PROFILE --------------------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    try:
        
        return Response({
            'message': 'Profile retrieved successfully',
            'data': {
            'id': request.user.id,
            'full_name': f"{request.user.first_name} {request.user.last_name}".strip(),
            'email': request.user.email,
            'username': request.user.username
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': str(e), 'message': 'Failed to retrieve profile'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ---------------------------------- RESET PASSWORD --------------------------------------

@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    try:
        email = request.data.get('email')

        if not email:
            return Response({'error': 'Email is required'}, status=400)

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({'error': 'User with this email does not exist'}, status=404)

        otp = generate_otp()

        EmailOTP.objects.filter(user=user, purpose='reset').delete()
        EmailOTP.objects.create(user=user, otp=otp, purpose='reset')

        send_mail(
            subject='Password Reset OTP',
            message=f'Your password reset OTP is {otp}. It is valid for 5 minutes.',
            from_email=None,
            recipient_list=[user.email],
        )

        return Response({'message': 'Password reset OTP sent to email'})
    except Exception as e:
        return Response(
            {'error': str(e), 'message': 'Failed to send password reset OTP'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ------------------------------------ VERIFY RESET OTP --------------------------------------

@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_verify_otp(request):
    try:
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email or not otp:
            return Response({'error': 'Email and OTP are required'}, status=400)

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({'error': 'Invalid email'}, status=400)

        otp_obj = EmailOTP.objects.filter(
            user=user,
            otp=otp,
            purpose='reset',
            is_used=False
        ).last()

        if not otp_obj:
            return Response({'error': 'Invalid OTP'}, status=400)

        if otp_obj.is_expired():
            return Response({'error': 'OTP expired'}, status=400)

        otp_obj.is_used = True
        otp_obj.save()

        return Response({'message': 'OTP verified. You may now reset your password'})
    except Exception as e:
        return Response(
            {'error': str(e), 'message': 'Failed to verify OTP'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ---------------------------------------- CONFIRM RESET PASSWORD --------------------------------

@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    try:
        email = request.data.get('email')
        new_password = request.data.get('new_password')

        if not email or not new_password:
            return Response({'error': 'Email and new password are required'}, status=400)

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({'error': 'Invalid email'}, status=400)

        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return Response({'error': e.messages}, status=400)

        user.set_password(new_password)
        user.save()

        return Response({'message': 'Password reset successful.'})
    except Exception as e:
        return Response(
            {'error': str(e), 'message': 'Failed to reset password'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ----------------------Update Profile Text Data Only----------------
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    try:
        user = request.user
        serializer = ProfileSerializer(
            user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Profile updated successfully', 'data': serializer.data})
    except Exception as e:
        return Response(
            {'error': str(e), 'message': 'Failed to update profile'},
            status=status.HTTP_400_BAD_REQUEST
        )


# -----------------------------UPLOAD PROFILE PICTURE (MULTIPART)----------------

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_avatar(request):
    try:
        user = request.user
        file = request.FILES.get('profile_image')

        if not file:
            return Response(
                {'error': 'No file provided'},
                status=400
            )

        user.profile_image = file
        user.save()

        return Response({
            'message': 'Profile picture updated successfully',
            'profile_image_url': request.build_absolute_uri(
                user.profile_image.url
            )
        })
    except Exception as e:
        return Response(
            {'error': str(e), 'message': 'Failed to upload profile picture'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
