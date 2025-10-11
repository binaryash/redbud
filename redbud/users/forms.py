#!/usr/bin/env python3

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Training, TrainingModule


class UserRegistrationForm(UserCreationForm):
    """
    Form for user registration
    """
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'role', 'password1', 'password2']


class LoginForm(forms.Form):
    """
    Form for user login
    """
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)


class TrainingForm(forms.ModelForm):
    """
    Form for creating/editing trainings
    """
    class Meta:
        model = Training
        fields = ['name', 'description', 'start_date', 'end_date', 'duration_days', 'assigned_trainer', 'employees', 'is_active']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class TrainingModuleForm(forms.ModelForm):
    """
    Form for creating/editing training modules
    """
    class Meta:
        model = TrainingModule
        fields = ['title', 'description', 'order', 'duration_hours']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
