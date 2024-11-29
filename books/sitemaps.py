from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Book

class BookSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return Book.objects.all()

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return reverse('books:detail', args=[obj.pk])


class StaticBookSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return ["books:index"]

    def location(self, item):
        return reverse(item)
