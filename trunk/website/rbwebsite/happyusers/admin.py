from django.contrib import admin

from rbwebsite.happyusers.models import HappyUserGroup, HappyUser


class HappyUserGroupAdmin(admin.ModelAdmin):
    list_display = ('name',)


class HappyUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'group')


admin.site.register(HappyUserGroup, HappyUserGroupAdmin)
admin.site.register(HappyUser, HappyUserAdmin)
