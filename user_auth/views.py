from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db.models.query import RawQuerySet
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import FormView, CreateView, View

from books.views import TokenMixin
from user_auth.forms import LoginForm, RegisterForm


class UserLoginView(TokenMixin, FormView):
    template_name = 'user_auth/user_login.html'
    form_class = LoginForm
    model = User
    object = None
    success_url = reverse_lazy('books:index')

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            db_query = f"SELECT * FROM {self.model._meta.db_table} WHERE username = %s"
            founded_users = self.model.objects.raw(db_query, [username])

            if len(founded_users) == 0:
                raise Http404("Пользователь не найден")

            user = founded_users[-1]

            if not user.check_password(password):
                raise ValidationError("Не верный пароль", code=403)

            self.object = user
            token = self.generate_token(request.user)

            response = HttpResponseRedirect(self.get_success_url())
            response.set_cookie("token", token)

            return response

        else:
            return self.form_invalid(form)


class UserRegistrationView(TokenMixin, CreateView):
    template_name = 'user_auth/user_register.html'
    form_class = RegisterForm
    object = None
    model = User
    success_url = reverse_lazy("books:index")

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if not form.is_valid():
            return self.form_invalid(form)

        self.object = form.save(commit=False)
        self.object.set_password(self.object.password)
        self.object.save()

        token = self.generate_token(self.object)

        response = HttpResponseRedirect(self.get_success_url())
        response.set_cookie("token", token)

        return response


class UserLogoutView(TokenMixin, View):
    success_url = reverse_lazy("books:index")

    def get(self, request, *args, **kwargs):
        token = self.check_token(request.COOKIES.get("token"))

        response = HttpResponseRedirect(self.success_url)
        response.delete_cookie("token")

        return response




