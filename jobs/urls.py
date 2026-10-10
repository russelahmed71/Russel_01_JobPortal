from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('job/new/', views.job_create, name='job_create'),
    path('search/', views.job_search_view, name='job_search'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('job/apply/<int:job_id>/', views.apply_job, name='apply_job'), 
    ]
