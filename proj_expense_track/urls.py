
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/account/', include('account.urls')),
    path('api/usersettings/', include('usersettings.urls')),
    path('api/budgets/', include('api_budgets.urls')),
    path('api/expenses/', include('api_expenses.urls')),
    path('api/dashboard/', include('dashboard.urls')),
    path('api/contact/', include('contact.urls')),
]

from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
