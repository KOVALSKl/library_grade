from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import Http404, JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.generic import FormView, TemplateView, CreateView
from django.views.generic.edit import ModelFormMixin
from rest_framework_simplejwt.tokens import RefreshToken

from user_auth.forms import LoginForm, RegisterForm


class UserLoginView(FormView):
    template_name = 'user_auth/user_login.html'
    form_class = LoginForm
    model = User

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            users_filter = (Q(username=username))
            founded_users = self.model.objects.filter(users_filter)

            if not founded_users.exists():
                raise Http404("Пользователь не найден")

            user = founded_users.last()

            if not user.check_password(password):
                raise ValidationError("Не верный пароль", code=403)

            self.object = user
            token = RefreshToken.for_user(self.object)
            response = HttpResponse({
                "token": str(token),
            })
            response.set_cookie("token", str(token), token.lifetime, secure=True)

            return response

        else:
            return self.form_invalid(form)


class UserRegistrationView(CreateView):
    template_name = 'user_auth/user_register.html'
    form_class = RegisterForm
    object = None
    model = User

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if not form.is_valid():
            return self.form_invalid(form)

        self.object = form.save(commit=False)
        self.object.set_password(self.object.password)
        self.object.save()

        token = RefreshToken.for_user(self.object)
        response = HttpResponse({
            "token": str(token),
        })
        response.set_cookie("token", str(token), token.lifetime, secure=True)

        return response




