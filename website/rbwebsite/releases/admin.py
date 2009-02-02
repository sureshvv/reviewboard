from django.contrib import admin

from rbwebsite.releases.models import Product, Release


class ProductAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'visible', 'third_party')
    list_filter = ('visible', 'third_party')


class ReleaseAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'scm_revision')
    list_filter = ('product', 'major_version', 'release_type')


admin.site.register(Product, ProductAdmin)
admin.site.register(Release, ReleaseAdmin)
