from django.contrib import sitemaps
from django.urls import reverse

class StaticAuthSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = "never"

    def items(self):
        return ["user_auth:login", "user_auth:registration"]

    def location(self, item):
        return reverse(item)
