from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404, \
                        HttpResponseForbidden
from django.shortcuts import get_object_or_404, render_to_response
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.translation import ugettext as _
from django.views.decorators.cache import cache_control
from django.views.generic.list_detail import object_list

from djblets.auth.util import login_required
from djblets.util.misc import get_object_or_none

from reviewboard.accounts.decorators import check_login_required, \
                                            valid_prefs_required
from reviewboard.accounts.models import Profile, ReviewRequestVisit
from reviewboard.datagrid.views import sortable_object_list
from reviewboard.diffviewer.forms import UploadDiffForm
from reviewboard.diffviewer.models import DiffSet
from reviewboard.diffviewer.views import view_diff, view_diff_fragment
from reviewboard.reviews.models import ReviewRequest, ReviewRequestDraft, \
                                       Review, Group, Screenshot, \
                                       ScreenshotComment
from reviewboard.reviews.forms import NewReviewRequestForm, \
                                      UploadScreenshotForm
from reviewboard.reviews.email import mail_review_request
from reviewboard.scmtools.models import Repository


@login_required
def new_review_request(request,
                       template_name='reviews/new_review_request.html'):
    """
    Displays a New Review Request form and handles the creation of a
    review request based on either an existing changeset or the provided
    information.
    """
    if request.method == 'POST':
        form = NewReviewRequestForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                review_request = form.create(request.user,
                                             request.FILES['diff_path'])
                return HttpResponseRedirect(review_request.get_absolute_url())
            except:
                # XXX - OwnershipError or ChangeSetError?
                #
                # We're preventing an exception from being thrown here so that
                # we can display the errors that form.create() sets in
                # a much nicer way in the template. Otherwise, the user would
                # see a useless backtrace.
                pass
    else:
        form = NewReviewRequestForm()

    # Repository ID : visible fields mapping.  This is so we can dynamically
    # show/hide the relevant fields with javascript.
    fields = {}
    for repo in Repository.objects.all():
        fields[repo.id] = repo.get_scmtool().get_fields()

    # Turn the selected index back into an int so we can compare it properly.
    if 'repository' in form.data:
        form.data['repository'] = int(form.data['repository'])

    return render_to_response(template_name, RequestContext(request, {
        'form': form,
        'fields': simplejson.dumps(fields),
    }))


@check_login_required
@cache_control(no_cache=True, no_store=True, max_age=0, must_revalidate=True)
def review_detail(request, review_request_id, template_name):
    """
    Main view for review requests. This covers the review request information
    and all the reviews on it.
    """
    review_request = get_object_or_404(ReviewRequest, pk=review_request_id)

    draft = get_object_or_none(review_request.reviewrequestdraft_set)
    reviews = review_request.review_set.filter(public=True,
                                               base_reply_to__isnull=True)
    for review in reviews:
        review.ordered_comments = \
            review.comments.order_by('filediff', 'first_line')

    # If the review request is public and pending review and if the user
    # is logged in, mark that they've visited this review request.
    if review_request.public and review_request.status == "P" and \
       request.user.is_authenticated():
        visited, visited_is_new = ReviewRequestVisit.objects.get_or_create(
            user=request.user, review_request=review_request)
        visited.timestamp = datetime.now()
        visited.save()

    repository = review_request.repository

    return render_to_response(template_name, RequestContext(request, {
        'draft': draft,
        'review_request': review_request,
        'review_request_details': draft or review_request,
        'reviews': reviews,
        'request': request,
        'upload_diff_form': UploadDiffForm(repository),
        'upload_screenshot_form': UploadScreenshotForm(),
        'scmtool': repository.get_scmtool(),
    }))


def review_list(request, queryset, template_name, default_filter=True,
                allow_hide_submitted=True, extra_context={}, **kwargs):
    """
    Convenience function for listing several reviwe requests, taking into
    account sort orders, the Show Submitted flag, and changes to either
    of these.
    """
    profile = None
    sort_columns = "-last_updated"
    show_submitted = True

    if request.user.is_authenticated():
        profile, profile_is_new = \
            Profile.objects.get_or_create(user=request.user)
        sort_columns = profile.sort_review_request_columns or sort_columns
        show_submitted = profile.show_submitted

    if default_filter:
        queryset = queryset.filter(Q(status='P') |
                                   Q(status='S')).order_by('-last_updated')

    sort = request.GET.get('sort', sort_columns)
    show_submitted = int(request.GET.get('show_submitted', show_submitted))

    extra_context['show_submitted'] = show_submitted

    if allow_hide_submitted and not show_submitted:
        queryset = queryset.exclude(Q(status='S'))

    response = sortable_object_list(request,
        queryset=queryset,
        default_sort=sort_columns,
        template_name=template_name,
        extra_context=extra_context,
        **kwargs)

    if profile and \
       (profile.sort_review_request_columns != sort or \
        profile.show_submitted != show_submitted):
        # Something in the profile changed, so save the change.
        profile.sort_review_request_columns = sort
        profile.show_submitted = show_submitted
        profile.save()

    return response


@check_login_required
def all_review_requests(request, template_name='reviews/review_list.html'):
    """
    Displays a list of all review requests.
    """
    return review_list(request,
        queryset=ReviewRequest.objects.public(request.user, status=None),
        template_name=template_name)


@check_login_required
def submitter_list(request, template_name='reviews/submitter_list.html'):
    """
    Displays a list of all users.
    """
    return object_list(request,
        queryset=User.objects.filter(),
        template_name=template_name,
        paginate_by=50,
        allow_empty=True,
        extra_context={
            'app_path': request.path,
        })


@check_login_required
def group_list(request, queryset=None, extra_context={},
               template_name='reviews/group_list.html'):
    """
    Displays a list of all review groups.
    """
    return object_list(request,
        queryset=queryset or Group.objects.all(),
        template_name=template_name,
        template_object_name='group',
        paginate_by=50,
        allow_empty=True,
        extra_context=dict({
            'app_path': request.path,
        }, **extra_context))


@login_required
@valid_prefs_required
def dashboard(request, template_name='reviews/dashboard.html'):
    """
    The dashboard view, showing review requests organized by a variety of
    lists, depending on the 'view' parameter.

    Valid 'view' parameters are:

        * 'outgoing'
        * 'to-me'
        * 'to-group'
        * 'starred'
        * 'watched-groups'
        * 'incoming'
    """
    view = request.GET.get('view', 'incoming')
    group = request.GET.get('group', "")
    user = request.user

    if view == 'outgoing':
        review_requests = ReviewRequest.objects.from_user(user.username, user)
        title = _(u"All Outgoing Review Requests")
    elif view == 'to-me':
        review_requests = \
            ReviewRequest.objects.to_user_directly(user.username, user)
        title = _(u"Incoming Review Requests to Me")
    elif view == 'to-group':
        if group != "":
            review_requests = ReviewRequest.objects.to_group(group, user)
            title = _(u"Incoming Review Requests to %s") % group
        else:
            review_requests = \
                ReviewRequest.objects.to_user_groups(user.username, user)
            title = _(u"All Incoming Review Requests to My Groups")
    elif view == 'starred':
        review_requests = \
            user.get_profile().starred_review_requests.public(user)
        title = _(u"Starred Review Requests")
    elif view == 'watched-groups':
        # This is special. We want to return a list of groups, not
        # review requests.
        return group_list(request,
            queryset=user.get_profile().starred_groups.all(),
            template_name=template_name,
            extra_context={
                'title': _(u"Watched Groups"),
                'view': view,
                'group': group,
            })
    else: # "incoming" or invalid
        review_requests = ReviewRequest.objects.to_user(user.username, user)
        title = _(u"All Incoming Review Requests")

    return review_list(request,
        queryset=review_requests,
        template_name=template_name,
        default_filter=False,
        template_object_name='review_request',
        allow_hide_submitted=False,
        extra_context={
            'title': title,
            'view': view,
            'group': group,
        })


@check_login_required
def group(request, name, template_name='reviews/review_list.html'):
    """
    A list of review requests belonging to a particular group.
    """
    # Make sure the group exists
    get_object_or_404(Group, name=name)

    return review_list(request,
        queryset=ReviewRequest.objects.to_group(name, status=None),
        template_name=template_name,
        extra_context={
            'source': name,
            'group': get_object_or_none(Group, name=name),
        })


@check_login_required
def submitter(request, username, template_name='reviews/review_list.html'):
    """
    A list of review requests owned by a particular user.
    """
    # Make sure the user exists
    get_object_or_404(User, username=username)

    return review_list(request,
        queryset=ReviewRequest.objects.from_user(username, status=None),
        template_name=template_name,
        extra_context={
            'source': username + "'s",
        })


def _query_for_diff(review_request, revision, query_extra=None):
    """
    Queries for a diff based on several parameters.

    If the draft does not exist, this throws an Http404 exception.
    """

    # This will try to grab the diff associated with a draft if the review
    # request has an associated draft and is either the revision being
    # requested or no revision is being requested.
    draft = get_object_or_none(review_request.reviewrequestdraft_set)
    if draft and draft.diffset and \
       (revision is None or draft.diffset.revision == revision):
        return draft.diffset

    query = Q(history=review_request.diffset_history)

    # Grab a revision if requested.
    if revision is not None:
        query = query & Q(revision=revision)

    # Anything else the caller wants.
    if query_extra:
        query = query & query_extra

    try:
        return DiffSet.objects.filter(query).latest()
    except DiffSet.DoesNotExist:
        raise Http404


@check_login_required
def diff(request, review_request_id, revision=None, interdiff_revision=None,
         template_name='diffviewer/view_diff.html'):
    """
    A wrapper around diffviewer.views.view_diff that handles querying for
    diffs owned by a review request,taking into account interdiffs and
    providing the user's current review of the diff if it exists.
    """
    review_request = get_object_or_404(ReviewRequest, pk=review_request_id)
    diffset = _query_for_diff(review_request, revision)

    interdiffset_id = None
    review = None

    if interdiff_revision and interdiff_revision != revision:
        # An interdiff revision was specified. Try to find a matching
        # diffset.
        interdiffset = _query_for_diff(review_request, interdiff_revision)
        interdiffset_id = interdiffset.id

    if request.user.is_authenticated():
        # Try to find an existing pending review of this diff from the
        # current user.
        review = get_object_or_none(Review,
                                    user=request.user,
                                    review_request=review_request,
                                    public=False,
                                    base_reply_to__isnull=True)

    draft = get_object_or_none(review_request.reviewrequestdraft_set)
    repository = review_request.repository

    return view_diff(request, diffset.id, interdiffset_id, {
        'review': review,
        'review_request': review_request,
        'review_request_details': draft or review_request,
        'upload_diff_form': UploadDiffForm(repository),
        'upload_screenshot_form': UploadScreenshotForm(),
        'scmtool': repository.get_scmtool(),
    }, template_name)


@check_login_required
def raw_diff(request, review_request_id, revision=None):
    """
    Displays a raw diff of all the filediffs in a diffset for the
    given review request.
    """
    review_request = get_object_or_404(ReviewRequest, pk=review_request_id)
    diffset = _query_for_diff(review_request, revision)

    data = ''.join([filediff.diff for filediff in diffset.files.all()])

    resp = HttpResponse(data, mimetype='text/x-patch')
    resp['Content-Disposition'] = 'inline; filename=%s' % diffset.name
    return resp


@check_login_required
def diff_fragment(request, review_request_id, revision, filediff_id,
                  interdiffset_id=None, chunkindex=None, collapseall=False,
                  template_name='diffviewer/diff_file_fragment.html'):
    """
    Wrapper around diffviewer.views.view_diff_fragment that takes a review
    request.

    Displays just a fragment of a diff or interdiff owned by the given
    review request. The fragment is identified by the chunk index in the
    diff.
    """
    review_request = get_object_or_404(ReviewRequest, pk=review_request_id)

    try:
        draft = review_request.reviewrequestdraft_set.get()
        query_extra = Q(reviewrequestdraft=draft)
    except ReviewRequestDraft.DoesNotExist:
        query_extra = None

    diffset = _query_for_diff(review_request, revision, query_extra)

    return view_diff_fragment(request, diffset.id, filediff_id,
                              interdiffset_id, chunkindex, collapseall,
                              template_name)


@login_required
def publish(request, review_request_id):
    """
    Publishes a new review request or the changes on a draft for a review
    request.
    """
    review_request = get_object_or_404(ReviewRequest, pk=review_request_id)

    if review_request.submitter == request.user:
        if not review_request.target_groups and \
           not review_request.target_people:
            pass # FIXME show an error

        review_request.public = True

        try:
            draft = review_request.reviewrequestdraft_set.get()

            # This will in turn save the review request, so we'll be done.
            draft.save_draft()

            # Make sure we have the draft's copy of the review request.
            review_request = draft.review_request

            # We don't need this anymore.
            draft.delete()
        except ReviewRequestDraft.DoesNotExist:
            # The draft didn't exist, so we must save the review request
            # ourselves.
            review_request.save()

        if settings.SEND_REVIEW_MAIL:
            mail_review_request(request.user, review_request)

        return HttpResponseRedirect(review_request.get_absolute_url())
    else:
        raise HttpResponseForbidden() # XXX Error out


@login_required
def setstatus(request, review_request_id, action):
    """
    Sets the status of the review request based on the specified action.

    Valid actions are:

        * 'discard'
        * 'submitted'
        * 'reopen'

    If a review request was discarded and action is 'reopen', this will
    reset the review request's public state to False.

    If the user is not the owner of this review request and does not have
    the 'reviews.can_change_status' permission, they will get an
    HTTP Forbidden error.
    """
    review_request = get_object_or_404(ReviewRequest, pk=review_request_id)

    if request.user != review_request.submitter and \
       not request.user.has_perm("reviews.can_change_status"):
        raise HttpResponseForbidden()

    try:
        if review_request.status == "D" and action == "reopen":
            review_request.public = False

        review_request.status = {
            'discard':   'D',
            'submitted': 'S',
            'reopen':    'P',
        }[action]

    except KeyError:
        # This should never happen under normal circumstances
        raise Exception('Error when setting review status: unknown status code')

    review_request.save()
    if action == 'discard':
        return HttpResponseRedirect('/dashboard/')
    else:
        return HttpResponseRedirect(review_request.get_absolute_url())


@check_login_required
def preview_review_request_email(
        request, review_request_id,
        template_name='reviews/review_request_email.txt'):
    """
    Previews the e-mail message that would be sent for an initial
    review request or an update.

    This is mainly used for debugging.
    """
    review_request = get_object_or_404(ReviewRequest, pk=review_request_id)

    return HttpResponse(render_to_string(template_name,
        RequestContext(request, {
            'review_request': review_request,
            'user': request.user,
            'domain': Site.objects.get(pk=settings.SITE_ID).domain,
            'domain_method': settings.DOMAIN_METHOD,
        }),
    ), mimetype='text/plain')


@check_login_required
def preview_review_email(request, review_request_id, review_id,
                         template_name='reviews/review_email.txt'):
    """
    Previews the e-mail message that would be sent for a review of a
    review request.

    This is mainly used for debugging.
    """
    review_request = get_object_or_404(ReviewRequest, pk=review_request_id)
    review = get_object_or_404(Review, pk=review_id,
                               review_request=review_request)

    review.ordered_comments = \
        review.comments.order_by('filediff', 'first_line')

    return HttpResponse(render_to_string(template_name,
        RequestContext(request, {
            'review_request': review_request,
            'review': review,
            'user': request.user,
            'domain': Site.objects.get(pk=settings.SITE_ID).domain,
            'domain_method': settings.DOMAIN_METHOD,
        }),
    ), mimetype='text/plain')


@check_login_required
def preview_reply_email(request, review_request_id, review_id, reply_id,
                        template_name='reviews/reply_email.txt'):
    """
    Previews the e-mail message that would be sent for a reply to a
    review of a review request.

    This is mainly used for debugging.
    """
    review_request = get_object_or_404(ReviewRequest, pk=review_request_id)
    review = get_object_or_404(Review, pk=review_id,
                               review_request=review_request)
    reply = get_object_or_404(Review, pk=reply_id, base_reply_to=review)

    return HttpResponse(render_to_string(template_name,
        RequestContext(request, {
            'review_request': review_request,
            'review': review,
            'reply': reply,
            'user': request.user,
            'domain': Site.objects.get(pk=settings.SITE_ID).domain,
            'domain_method': settings.DOMAIN_METHOD,
        }),
    ), mimetype='text/plain')


@login_required
def delete_screenshot(request, review_request_id, screenshot_id):
    """
    Deletes a screenshot from a review request and redirects back to the
    review request page.
    """
    request = get_object_or_404(ReviewRequest, pk=review_request_id)

    s = Screenshot.objects.get(id=screenshot_id)

    draft = ReviewRequestDraft.create(request)
    draft.screenshots.remove(s)
    draft.inactive_screenshots.add(s)
    draft.save()

    return HttpResponseRedirect(request.get_absolute_url())


@check_login_required
def view_screenshot(request, review_request_id, screenshot_id,
                    template_name='reviews/screenshot_detail.html'):
    review_request = get_object_or_404(ReviewRequest, pk=review_request_id)
    screenshot = get_object_or_404(Screenshot, pk=screenshot_id)

    query = Q(history=review_request.diffset_history)

    draft = get_object_or_none(review_request.reviewrequestdraft_set)
    if draft:
        query = query & Q(reviewrequestdraft=draft)

    try:
        diffset = DiffSet.objects.filter(query).latest()
    except DiffSet.DoesNotExist:
        diffset = None

    try:
        comments = ScreenshotComment.objects.filter(screenshot=screenshot)
    except ScreenshotComment.DoesNotExist:
        comments = []

    return render_to_response(template_name, RequestContext(request, {
        'draft': draft,
        'review_request': review_request,
        'details': draft or review_request,
        'screenshot': screenshot,
        'request': request,
        'diffset': diffset,
        'comments': comments,
    }))
