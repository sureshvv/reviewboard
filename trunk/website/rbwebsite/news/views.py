from datetime import datetime
from xmlrpclib import loads, dumps, Fault, ResponseError, DateTime

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseNotAllowed
from django.utils.html import strip_spaces_between_tags
from django.views.generic.list_detail import object_list

from rbwebsite.news.models import Category, NewsPost


METHOD_NOT_SUPPORTED = Fault(0, "Method not supported")
BAD_LOGIN_PASS       = Fault(403, "Authentication failed")
NO_SUCH_PAGE         = Fault(404, "Page not found")


def category_posts(request, slug, queryset, extra_context, template_name):
    return object_list(request,
                       queryset.filter(categories__slug=slug),
                       extra_context=extra_context,
                       template_name=template_name)


def get_user(username, password):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise BAD_LOGIN_PASS

    if not user.check_password(password):
        raise BAD_LOGIN_PASS

    return user


def get_post(post_id):
    try:
        return NewsPost.objects.get(pk=post_id)
    except NewsPost.DoesNotExist:
        raise NO_SUCH_PAGE


def serialize_post(post):
    link = "http://%s%s" % (Site.objects.get_current().domain,
                            post.get_absolute_url())

    return {
        'postid': post.id,
        'title': post.title,
        'link': link,
        'permaLink': link,
        'description': post.content,
        'categories': [category.name for category in post.categories.all()],
        'userid': post.author.id,
        'dateCreated': DateTime(post.timestamp.isoformat()),
    }


def blogger_delete_post(appkey, post_id, username, password, publish):
    user = get_user(username, password)
    post = get_post(post_id)
    post.delete()

    return True


def blogger_get_recent_posts(appkey, blog_id, username, password, num_posts):
    get_user(username, password)
    posts = NewsPost.objects.order_by('-timestamp')[:num_posts]
    return [serialize_post(post) for post in posts]


def blogger_get_users_blogs(appkey, username, password):
    get_user(username, password)

    return [{
        'url': reverse("news"),
        'blogid': settings.SITE_ID,
        'blogName': 'Review Board News'
    }]


def metaweblog_edit_post(post_id, username, password, content, publish):
    user = get_user(username, password)
    post = get_post(post_id)

    post.content = content['description']
    post.title = content['title']

    if publish:
        post.public = True

    post.save()

    return True


def metaweblog_get_post(post_id, username, password):
    user = get_user(username, password)
    return serialize_post(get_post(post_id))


def metaweblog_get_recent_posts(blog_id, username, password, num_posts):
    get_user(username, password)
    posts = NewsPost.objects.order_by('-timestamp')[:num_posts]
    return [serialize_post(post) for post in posts]


def metaweblog_new_post(blog_id, username, password, content, publish):
    user = get_user(username, password)

    post = NewsPost.objects.create(
        title=content['title'],
        content=content['description'],
        public=publish,
        timestamp=datetime.now(),
        author=user)
    post.save()

    return post.id


def mt_get_categories(blog_id, username, password):
    get_user(username, password)
    return [mt_serialize_category(category)
            for category in Category.objects.all()]


def mt_get_post_categories(post_id, username, password):
    get_user(username, password)
    post = get_post(post_id)
    return [mt_serialize_category(category)
            for category in post.categories.all()]


def mt_publish_post(post_id, username, password):
    get_user(username, password)
    post = get_post(post_id)

    if not post.public:
        post.public = True
        post.save()

    return True


def mt_set_post_categories(post_id, username, password, categories):
    get_user(username, password)
    post = get_post(post_id)
    post.categories = []

    for category in categories:
        post.categories.add(
            Category.objects.get(slug=category['categoryId']))

    post.save()

    return True


def mt_serialize_category(category):
    return {
        'categoryName': category.name,
        'categoryId': category.slug,
        'isPrimary': False,
    }


def xmlrpc(request):
    if request.method != "POST":
        return HttpResponseNotAllowed("POST")

    try:
        args, method = loads(request.raw_post_data)
    except ResponseError:
        return HttpResponseNotAllowed("XML-RPC")

    print "method: %s" % method
    #print "args: %s" % args

    if method is None:
        return HttpResponseNotAllowed("XML-RPC")

    if method in XMLRPC_HANDLERS:
        try:
            result = XMLRPC_HANDLERS[method](*args)
        except Fault, fault:
            result = fault
    else:
        print args
        result = METHOD_NOT_SUPPORTED

    if not isinstance(result, (tuple, Fault)):
        result = (result,)

    result = strip_spaces_between_tags(dumps(result, methodresponse=True))

    response = HttpResponse(mimetype="text/xml")
    response.write(result)
    response['Content-Length'] = len(response.content)
    return response


XMLRPC_HANDLERS = {
    'blogger.deletePost': blogger_delete_post,
    'blogger.getRecentPosts': blogger_get_recent_posts,
    'blogger.getUsersBlogs': blogger_get_users_blogs,
    'metaWeblog.editPost': metaweblog_edit_post,
    'metaWeblog.getRecentPosts': metaweblog_get_recent_posts,
    'metaWeblog.getPost': metaweblog_get_post,
    'metaWeblog.newPost': metaweblog_new_post,
    'mt.getCategoryList': mt_get_categories,
    'mt.getPostCategories': mt_get_post_categories,
    'mt.publishPost': mt_publish_post,
    'mt.setPostCategories': mt_set_post_categories,
}
