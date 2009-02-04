from django.contrib.sitemaps import Sitemap

from rbwebsite.news.models import NewsPost


class NewsSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        return NewsPost.objects.filter(public=True)

    def lastmod(self, obj):
        return obj.timestamp
