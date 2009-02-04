from datetime import datetime

from django.contrib.sitemaps import Sitemap


class PageSitemap(Sitemap):
    pages = {
        'Home': {
            'path': '/',
            'priority': 0.5,
            'changefreq': 'weekly',
        },
        'Donate': {
            'path': '/donate/',
            'priority': 0.6,
            'changefreq': 'monthly',
        },
        'Developer Blog': {
            'path': '/blog/',
            'priority': 0.8,
            'changefreq': 'weekly',
        },
        'Screenshots': {
            'path': '/screenshots/',
            'priority': 0.5,
            'changefreq': 'monthly',
        },
        'Press and Media': {
            'path': '/press/',
            'priority': 0.4,
            'changefreq': 'monthly',
        },
        'Downloads': {
            'path': '/downloads/',
            'priority': 0.6,
            'changefreq': 'monthly',
        },
        'Mailing Lists': {
            'path': '/mailing-lists/',
            'priority': 0.4,
            'changefreq': 'never',
        },
        'Happy Users': {
            'path': '/users/',
            'priority': 0.4,
            'changefreq': 'monthly',
        },
    }

    def items(self):
        return self.pages.keys()

    def location(self, key):
        return self.pages[key]['path']

    def lastmod(self, key):
        return datetime.now()

    def changefreq(self, key):
        return self.pages[key]['changefreq']

    def priority(self, key):
        return self.pages[key]['priority']
