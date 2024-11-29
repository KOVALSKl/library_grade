import pandas as pd
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

import logging

from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView, FormView
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import FormMixin
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from books.forms import BookForm, FileUploadForm
from books.models import Book
from books.tasks import process_books_data

logger = logging.getLogger(__name__)


class TokenValidationMixin:
    def check_token(self, token_str):
        if token_str is None:
            raise ValidationError("Необходимо зарегестрироваться или войти в акканут")

        token = RefreshToken(token_str)

        return token


class BookCreateView(TokenValidationMixin, FormMixin, TemplateResponseMixin, View):
    model = Book
    form_class = BookForm
    template_name = 'books/book_form.html'
    success_url = reverse_lazy("books:index")

    async def get(self, request, *args, **kwargs):
        token = self.check_token(request.COOKIES.get('token'))
        return self.render_to_response(self.get_context_data())

    async def post(self, request, *args, **kwargs):
        token = self.check_token(request.COOKIES.get('token'))

        form = self.get_form()

        if not form.is_valid():
            return self.form_invalid(form)

        self.object = form.save(commit=False)
        await self.object.asave()

        return HttpResponseRedirect(self.get_success_url())


class BookListingView(TemplateView):
    template_name = 'books/book_listing.html'
    model = Book

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        books = self.get_queryset()

        context["books"] = books

        return self.render_to_response(context)

    def get_queryset(self, **kwargs):
        if bool(kwargs):
            return self.model.objects.filter(**kwargs)

        return self.model.objects.all()


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


class BookImportView(TokenValidationMixin, FormMixin, TemplateResponseMixin, View):
    template_name = 'books/book_import.html'
    form_class = FileUploadForm
    success_url = reverse_lazy("books:index")

    async def get(self, request, *args, **kwargs):
        token = self.check_token(request.COOKIES.get('token'))
        return self.render_to_response(self.get_context_data())

    async def post(self, request, *args, **kwargs):
        form = self.get_form()

        if not form.is_valid():
            return self.form_invalid(form)

        uploaded_file = request.FILES['file']

        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(uploaded_file)
            else:
                return HttpResponse({'error': 'Unsupported file format'}, status=status.HTTP_400_BAD_REQUEST)

            data = df.to_dict(orient='records')
            task = process_books_data.delay(data)

            return HttpResponseRedirect(self.get_success_url())

        except Exception as e:
            print(e)
            return HttpResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
