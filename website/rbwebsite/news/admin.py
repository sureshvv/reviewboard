from django.contrib import admin

from rbwebsite.news.models import Category, Image, NewsPost


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {"slug": ("name",)}


class ImageAdmin(admin.ModelAdmin):
    list_display = ('caption', 'image', 'timestamp')


class NewsPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'timestamp')
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(Category, CategoryAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(NewsPost, NewsPostAdmin)
