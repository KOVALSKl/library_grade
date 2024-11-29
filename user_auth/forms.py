from django.contrib.auth.models import User
from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label="Имя пользователя")
    password = forms.CharField(
        widget=forms.PasswordInput,
        label="Пароль"
    )


class RegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password"]
