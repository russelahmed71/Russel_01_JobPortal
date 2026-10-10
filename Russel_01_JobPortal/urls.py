from django.contrib import admin
from django.urls import path, include
from jobs import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', views.login_view, name='login_fallback'),
    path('', include('jobs.urls')),
]
