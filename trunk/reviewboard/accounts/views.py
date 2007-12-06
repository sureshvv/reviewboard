from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from djblets.auth.util import login_required

from reviewboard.accounts.forms import PreferencesForm
from reviewboard.accounts.models import Profile


@login_required
def user_preferences(request, template_name='accounts/prefs.html'):
    redirect_to = request.REQUEST.get(REDIRECT_FIELD_NAME, '/')

    profile, profile_is_new = \
        Profile.objects.get_or_create(user=request.user)
    must_configure = not profile.first_time_setup_done
    profile.save()

    if request.POST:
        form = PreferencesForm(request.POST)

        if form.is_valid():
            request.user.group_set = form.cleaned_data['groups']
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.save()

            profile.first_time_setup_done = True
            profile.syntax_highlighting = \
                form.cleaned_data['syntax_highlighting']
            profile.save()

            return HttpResponseRedirect(redirect_to)

    else:
        form = PreferencesForm({
            'redirect_to': redirect_to,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'syntax_highlighting': profile.syntax_highlighting,
            'groups': [g.id for g in request.user.group_set.all()],
        })

    return render_to_response(template_name, RequestContext(request, {
        'form': form,
        'settings': settings,
        'must_configure': must_configure,
    }))