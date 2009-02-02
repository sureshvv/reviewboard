from django.contrib import admin

from rbwebsite.donations.models import FundRun, Goal, Donation


class FundRunAdmin(admin.ModelAdmin):
    list_display = ('name', 'goal', 'public')


class GoalAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'public')


class DonationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'amount', 'date')


admin.site.register(FundRun, FundRunAdmin)
admin.site.register(Goal, GoalAdmin)
admin.site.register(Donation, DonationAdmin)
