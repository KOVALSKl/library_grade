from django.urls import path

from .views import UserLoginView, UserRegistrationView, UserLogoutView

app_name = "user_auth"

urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    path("registration/", UserRegistrationView.as_view(), name="registration"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
]