import jwt
import pandas as pd
from django.conf import settings

import logging

from django.core.paginator import Paginator, PageNotAnInteger
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import FormMixin
from rest_framework import status

from books.forms import BookForm, FileUploadForm
from books.models import Book
from books.tasks import process_books_data

logger = logging.getLogger(__name__)


class TokenMixin:
    @staticmethod
    def generate_token(user):
        token = jwt.encode({
            "pk": user.pk,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "exp": settings.JWT_EXPIRATION_TIME,
        },
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM,
        )

        return token

    @staticmethod
    def check_token(token):
        try:
            decoded_token = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM]
            )
        except jwt.exceptions.PyJWTError as error:
            print(error)
            decoded_token = None

        return decoded_token


class BookCreateView(TokenMixin, FormMixin, TemplateResponseMixin, View):
    model = Book
    form_class = BookForm
    template_name = 'books/book_form.html'
    success_url = reverse_lazy("books:index")

    async def get(self, request, *args, **kwargs):
        token = self.check_token(request.COOKIES.get('token'))

        if token is None:
            return HttpResponse("Ошибка токена авторизации", status=status.HTTP_401_UNAUTHORIZED)

        return self.render_to_response(self.get_context_data())

    async def post(self, request, *args, **kwargs):
        token = self.check_token(request.COOKIES.get('token'))

        if token is None:
            return HttpResponse("Ошибка токена авторизации", status=status.HTTP_401_UNAUTHORIZED)

        form = self.get_form()

        if not form.is_valid():
            return self.form_invalid(form)

        self.object = form.save(commit=False)
        await self.object.asave()

        return HttpResponseRedirect(self.get_success_url())


class BookListingView(TokenMixin, TemplateView):
    template_name = 'books/book_listing.html'
    model = Book

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        books = self.get_queryset()

        limit = request.GET.get("limit", settings.PAGE_LIMIT)
        page_number = request.GET.get("page", 1)

        books_paginator = Paginator(books, limit)

        try:
            page = books_paginator.page(page_number)
        except PageNotAnInteger:
            page = books_paginator.page(1)

        token = self.check_token(request.COOKIES.get('token'))
        print(token)

        is_not_authorized = False

        if token is None:
            is_not_authorized = True

        context["is_not_authorized"] = is_not_authorized
        context["page_obj"] = page

        return self.render_to_response(context)

    def get_queryset(self, **kwargs):
        return self.model.objects.all().order_by("created_at")


class BookDetailView(TemplateView):
    model = Book
    template_name = 'books/book_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        book_id = kwargs.get('id', None)

        try:
            book = self.model.objects.get(pk=book_id)
        except self.model.DoesNotExist:
            logger.error(
                f"Объекта типа {self.model} с ключом {book_id} не существует"
            )
            raise Http404("Объекта не существует")

        context['book'] = book

        return context


class BookImportView(TokenMixin, FormMixin, TemplateResponseMixin, View):
    template_name = "books/book_import.html"
    form_class = FileUploadForm
    success_url = reverse_lazy("books:index")

    async def get(self, request, *args, **kwargs):
        token = self.check_token(request.COOKIES.get("token"))

        if token is None:
            return HttpResponse("Ошибка токена авторизации", status=status.HTTP_401_UNAUTHORIZED)

        return self.render_to_response(self.get_context_data())

    async def post(self, request, *args, **kwargs):
        form = self.get_form()

        if not form.is_valid():
            return self.form_invalid(form)

        uploaded_file = request.FILES["file"]

        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith((".xls", ".xlsx")):
                df = pd.read_excel(uploaded_file)
            else:
                return HttpResponse("Неподдерживаемый формат файла", status=status.HTTP_400_BAD_REQUEST)

            data = df.to_dict(orient='records')
            task = process_books_data.delay(data)

            return HttpResponseRedirect(self.get_success_url())

        except Exception as e:
            print(e)
            return HttpResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
