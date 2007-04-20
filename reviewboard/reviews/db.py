from django.db.models import Q

from reviewboard.diffviewer.models import DiffSetHistory
from reviewboard.reviews.models import ReviewRequest, Review
from reviewboard import scmtools

def _get_review_request_list(user, status, extra_query=None):
    query = (Q(public=True) | Q(submitter=user))

    if status != None:
        query = query & Q(status=status)

    if extra_query != None:
        query = extra_query & query

    return ReviewRequest.objects.filter(query).distinct()


def get_all_review_requests(user=None, status='P'):
    return _get_review_request_list(user, status)

def get_review_requests_to_group(group_name, user=None, status='P'):
    return _get_review_request_list(user, status,
                                    Q(target_groups__name=group_name))

def get_review_requests_to_user_groups(username, user=None, status='P'):
    return _get_review_request_list(user, status,
                                    Q(target_groups__users__username=username))

def get_review_requests_to_user_directly(username, user=None, status='P'):
    return _get_review_request_list(user, status,
                                    Q(target_people__username=username))

def get_review_requests_to_user(username, user=None, status='P'):
    return _get_review_request_list(user, status,
                                    Q(target_people__username=username) |
                                    Q(target_groups__users__username=username))

def get_review_requests_from_user(username, user=None, status='P'):
    return _get_review_request_list(user, status,
                                    Q(submitter__username=username))


class InvalidChangeNumberException(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)


def create_review_request(user, changenum=None):
    review_request = ReviewRequest()

    if changenum:
        changeset = scmtools.get_tool().get_changeset(changenum)

        if not changeset:
            raise InvalidChangeNumberException()

        review_request.changenum = changenum
        review_request.summary = changeset.summary
        review_request.description = changeset.description
        review_request.testing_done = changeset.testing_done
        review_request.branch = changeset.branch
        review_request.bugs_closed = ','.join(changeset.bugs_closed)

    diffset_history = DiffSetHistory()
    diffset_history.save()

    review_request.diffset_history = diffset_history
    review_request.submitter = user
    review_request.status = 'P'
    review_request.public = False
    review_request.save()

    return review_request
