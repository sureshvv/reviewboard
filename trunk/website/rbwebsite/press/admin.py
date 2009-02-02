from django.contrib import admin

from rbwebsite.press.models import PressGroup, PressItem


class PressGroupAdmin(admin.ModelAdmin):
    list_display = ('name',)


class PressItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'press_date', 'author', 'location', 'public',
                    'group')


admin.site.register(PressGroup, PressGroupAdmin)
admin.site.register(PressItem, PressItemAdmin)
