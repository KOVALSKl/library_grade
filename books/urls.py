from django.urls import path

from .views import BookListingView, BookDetailView, BookCreateView

app_name = "books"

urlpatterns = [
    path("", BookListingView.as_view() , name="index"),
    path("create", BookCreateView.as_view(), name="create"),
    path("<int:id>", BookDetailView.as_view() , name="detail"),
]