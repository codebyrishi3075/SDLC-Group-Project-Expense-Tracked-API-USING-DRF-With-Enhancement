from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'email',
        'username',
        'is_active',
        'is_email_verified',
        'is_staff',
        'is_superuser',
        'date_joined',
    )

    search_fields = ('email', 'username')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login')