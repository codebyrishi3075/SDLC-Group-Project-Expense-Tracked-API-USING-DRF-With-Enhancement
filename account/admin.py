from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, EmailOTP


# ═══════════════════════════════════════════════════════════
# CUSTOM USER ADMIN (CRITICAL FIX FOR PASSWORD HASHING)
# ═══════════════════════════════════════════════════════════

class CustomUserCreationForm(UserCreationForm):
    """Form for creating new users in admin panel"""
    class Meta:
        model = User
        fields = ('email', 'username')


class CustomUserChangeForm(UserChangeForm):
    """Form for updating users in admin panel"""
    class Meta:
        model = User
        fields = '__all__'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom UserAdmin that properly handles password hashing
    Inherits from Django's UserAdmin (NOT ModelAdmin)
    """
    
    # Forms for add and change pages
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    # List display in admin panel
    list_display = (
        'id',
        'email',
        'username',
        'first_name',
        'last_name',
        'is_active',
        'is_email_verified',
        'is_staff',
        'is_superuser',
        'date_joined',
    )
    
    # List filters
    list_filter = (
        'is_active',
        'is_staff',
        'is_superuser',
        'is_email_verified',
        'date_joined',
    )
    
    # Fields to show when editing existing user
    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        ('Personal Info', {
            'fields': ('username', 'first_name', 'last_name', 'profile_image')
        }),
        ('Permissions', {
            'fields': (
                'is_active',
                'is_email_verified',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    # Fields to show when creating new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'username',
                'password1',
                'password2',
                'first_name',
                'last_name',
            ),
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_email_verified', 'is_staff', 'is_superuser')
        }),
    )
    
    # Search functionality
    search_fields = ('email', 'username', 'first_name', 'last_name')
    
    # Default ordering
    ordering = ('-date_joined',)
    
    # Readonly fields
    readonly_fields = ('date_joined', 'last_login')
    
    # CRITICAL: This ensures password is hashed when saving
    def save_model(self, request, obj, form, change):
        """
        Override save to ensure passwords are hashed properly
        This is a safety net - the form should handle it, but this is extra protection
        """
        if not change:  # New user
            # For new users, password should already be hashed by the form
            # But we double-check just in case
            if obj.password and not obj.password.startswith('pbkdf2_'):
                obj.set_password(obj.password)
        
        super().save_model(request, obj, form, change)


# ═══════════════════════════════════════════════════════════
# EMAIL OTP ADMIN (OPTIONAL - FOR DEBUGGING)
# ═══════════════════════════════════════════════════════════

@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    """Admin interface for viewing OTPs (for debugging)"""
    
    list_display = (
        'id',
        'user',
        'otp',
        'purpose',
        'is_used',
        'created_at',
        'is_expired_status',
    )
    
    list_filter = ('purpose', 'is_used', 'created_at')
    search_fields = ('user__email', 'otp')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    def is_expired_status(self, obj):
        """Show if OTP is expired"""
        return obj.is_expired()
    
    is_expired_status.short_description = 'Expired?'
    is_expired_status.boolean = True


# ═══════════════════════════════════════════════════════════
# ADMIN SITE CUSTOMIZATION (OPTIONAL)
# ═══════════════════════════════════════════════════════════

admin.site.site_header = "Fin Pocket Admin"
admin.site.site_title = "Fin Pocket Admin Portal"
admin.site.index_title = "Welcome to Fin Pocket Administration"