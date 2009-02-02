from django.contrib import admin

from rbwebsite.blogfeeds.models import BlogFeed, BlogFeedPost


class BlogFeedAdmin(admin.ModelAdmin):
    list_display = ('author', 'site_url', 'feed_url')


class BlogFeedPostAdmin(admin.ModelAdmin):
    list_display = ('feed', 'title', 'timestamp')


admin.site.register(BlogFeed, BlogFeedAdmin)
admin.site.register(BlogFeedPost, BlogFeedPostAdmin)
