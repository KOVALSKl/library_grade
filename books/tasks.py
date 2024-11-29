import os

from celery import shared_task
from django.core.mail import send_mail

from .models import Book

@shared_task
def process_books_data(data):
    try:
        print("NIGGERS")
        books = [
            Book(
                title=entry.get('title'),
                description=entry.get('description'),
                year=entry.get('year'),
                image=None,
                rating=entry.get('rating'),
            )
            for entry in data
        ]

        Book.objects.bulk_create(books)

        message = ""
        for book in books:
            message += f"Была добавлена книга: {book!r}\n"

        try:
            send_mail(
                "Добавленные книги",
                message,
                "from@example.com",
                ["recipient@example.com"],
            )
        except Exception as e:
            print(e)

        return f"Successfully imported {len(books)} books."
    except Exception as e:
        return str(e)
