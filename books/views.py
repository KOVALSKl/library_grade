from django.shortcuts import render

import logging

from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView

from books.models import Book
from books.utils import FiltersToKwargs

logger = logging.getLogger(__name__)


class BookCreateView(CreateView):
    model = Book
    fields = '__all__'
    success_url = reverse_lazy("books:index")


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


