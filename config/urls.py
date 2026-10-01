"""
توجيه المسارات الرئيسي لمنظومة صرح القرآن الكريم
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', lambda request: redirect('accounts:dashboard_redirect'), name='root'),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('', include('academy.urls', namespace='academy')),
    path('attendance/', include('attendance.urls', namespace='attendance')),
    path('evaluations/', include('evaluations.urls', namespace='evaluations')),
    path('reports/', include('reports.urls', namespace='reports')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
