from django.urls import path

from .views import UserLoginView, UserRegistrationView

app_name = "user_auth"

urlpatterns = [
    path("login", UserLoginView.as_view(), name="login"),
    path("registration", UserRegistrationView.as_view(), name="registration"),
]