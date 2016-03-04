from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile


class UserCreateForm(UserCreationForm):
    avatar = forms.ImageField(label='Upload avatar', required=False)

    class Meta:
        model = User
        fields = ("username",)
