import cPickle as pickle
import os

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.static import serve


VERSIONS = settings.DOCS_ROOT.keys()


def get_doc_path(section, version, parts=[]):
    return os.path.join(settings.DOCS_ROOT[version], section,
                        "_build", "pickle",
                        *parts)

def index(request):
    return HttpResponseRedirect(
        reverse('doc-index', kwargs={
            'version': 'dev',
        })
    )


def document(request, section, version, path=""):
    if version not in VERSIONS:
        return Http404()

    path = path.strip("/")
    parts = path.split("/")

    pickle_root = get_doc_path(section, version)
    env_filename = os.path.join(pickle_root, "globalcontext.pickle")

    docroot = get_doc_path(section, version, parts)
    filename = os.path.join(docroot, "index.fpickle")

    if not os.path.exists(filename):
        filename = docroot + ".fpickle"

        if not os.path.exists(filename):
            raise Http404()

    template_names = [
        "docs/%s.html" % '-'.join(parts),
        "docs/docpage.html",
    ]
    return render_to_response(template_names, RequestContext(request, {
        'doc': pickle.load(open(filename, "rb")),
        'env': pickle.load(open(env_filename, "rb")),
        'home': reverse('doc-section-index', kwargs={
            'section': section,
            'version': version,
        }),
        'section': section,
        'version': version,
    }))


def images(request, section, version, path):
    if version not in VERSIONS:
        return Http404()

    return serve(
        request,
        document_root=os.path.join(get_doc_path(section, version), "_images"),
        path=path)


def source(request, section, version, path):
    if version not in VERSIONS:
        return Http404()

    return serve(
        request,
        document_root=os.path.join(get_doc_path(section, version), "_sources"),
        path=path)


def objects_inv(request, section, version):
    if version not in VERSIONS:
        return Http404()

    return serve(
        request,
        document_root=os.path.join(get_doc_path(section, version)),
        path='objects.inv')
