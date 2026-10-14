from django import forms
from django.contrib.auth import get_user_model
from .models import Job

User = get_user_model()

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'user_type']
        help_texts = {
            'username': None,
        }

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'category', 'description', 'skills_required']
