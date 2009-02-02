from django.contrib import admin

from rbwebsite.screenshots.models import Screenshot


class ScreenshotAdmin(admin.ModelAdmin):
    list_display = ('thumb', 'caption', 'public', 'timestamp')
    list_filter = ('public', 'timestamp')


admin.site.register(Screenshot, ScreenshotAdmin)
