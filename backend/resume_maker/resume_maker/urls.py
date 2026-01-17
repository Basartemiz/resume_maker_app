"""
URL configuration for resume_maker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


def health_check(request):
    """Health check endpoint for DigitalOcean."""
    return JsonResponse({"status": "ok"})


# Custom token views with explicit AllowAny permission
class PublicTokenObtainPairView(TokenObtainPairView):
    """Login endpoint - public access allowed."""
    permission_classes = [AllowAny]


class PublicTokenRefreshView(TokenRefreshView):
    """Token refresh endpoint - public access allowed."""
    permission_classes = [AllowAny]


urlpatterns = [
    # Health check - ingress strips /api prefix, so this becomes /health/
    path('health/', health_check, name='health_check'),

    path('admin/', admin.site.urls),

    # Resume endpoints - ingress strips /resume prefix
    path('', include('resume.urls')),

    # Auth endpoints - ingress strips /api prefix
    path('token/', PublicTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', PublicTokenRefreshView.as_view(), name='token_refresh'),

    # Register endpoint - ingress strips /register prefix
    path('', include('register.urls')),
]
