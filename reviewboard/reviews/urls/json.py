from django.conf.urls.defaults import *
from reviewboard.reviews.db import *

urlpatterns = patterns('reviewboard.reviews.json',
    # Review request lists
    (r'^reviewrequests/all/$', 'review_request_list',
     {'func': get_all_review_requests}),
    (r'^reviewrequests/all/count/$', 'count_review_requests',
     {'func': get_all_review_requests}),

    (r'^reviewrequests/to/group/(?P<group_name>[A-Za-z0-9_-]+)/$',
     'review_request_list',
     {'func': get_review_requests_to_group}),
    (r'^reviewrequests/to/group/(?P<group_name>[A-Za-z0-9_-]+)/count/$',
     'count_review_requests',
     {'func': get_review_requests_to_group}),

    (r'^reviewrequests/to/user/(?P<username>[A-Za-z0-9_-]+)/$',
     'review_request_list',
     {'func': get_review_requests_to_user}),
    (r'^reviewrequests/to/user/(?P<username>[A-Za-z0-9_-]+)/count/$',
     'count_review_requests',
     {'func': get_review_requests_to_user}),

    (r'^reviewrequests/from/user/(?P<username>[A-Za-z0-9_-]+)/$',
     'review_request_list',
     {'func': get_review_requests_from_user}),
    (r'^reviewrequests/from/user/(?P<username>[A-Za-z0-9_-]+)/count/$',
     'count_review_requests',
     {'func': get_review_requests_from_user}),

    # Review requests
    (r'^reviewrequests/(?P<object_id>[0-9]+)/$', 'serialized_object',
     {'queryset': ReviewRequest.objects.all(),
      'varname': 'review_request'}),
    (r'^reviewrequests/(?P<review_request_id>[0-9]+)/draft/set/(?P<field_name>[A-Za-z0-9_-]+)/$',
     'review_request_draft_set'),

    # Reviews
    (r'^reviewrequests/(?P<review_request_id>[0-9]+)/reviews/draft/save/$',
     'review_draft_save'),
    (r'^reviewrequests/(?P<review_request_id>[0-9]+)/reviews/draft/publish/$',
     'review_draft_save',
     {'publish': True}),
    (r'^reviewrequests/(?P<review_request_id>[0-9]+)/reviews/draft/delete/$',
     'review_draft_delete'),
    (r'^reviewrequests/(?P<review_request_id>[0-9]+)/reviews/draft/comments/$',
     'review_draft_comments'),

    # Replies
)
