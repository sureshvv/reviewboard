from django.shortcuts import render_to_response
from django.template.context import RequestContext

from rbwebsite.donations.models import Donation, FundRun, Goal


def donate_page(request, template_name="rbwebsite/donate.html"):
    fund_run = FundRun.objects.filter(public=True)[0]
    goals = Goal.objects.filter(public=True)
    donations = Donation.objects.all()

    donation_total = 0

    for donation in donations:
        donation_total += donation.amount

    cur_pct = float(donation_total) / float(fund_run.goal) * 100;

    empty_pct = 100 - cur_pct

    for goal in goals:
        goal.top = 100 - float(goal.amount) / float(fund_run.goal) * 100

    return render_to_response(template_name, RequestContext(request, {
        'goals': goals,
        'empty_pct': empty_pct,
        'cur_pct': cur_pct,
        'goal_total': fund_run.goal,
        'donation_total': donation_total,
    }))
