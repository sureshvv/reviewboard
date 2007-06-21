import traceback

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from djblets.util.misc import cache_memoize

from reviewboard.diffviewer.forms import UploadDiffForm
from reviewboard.diffviewer.models import DiffSet, FileDiff, DiffSetHistory
from reviewboard.scmtools.models import Repository
import reviewboard.diffviewer.diffutils as diffutils
import reviewboard.scmtools as scmtools


class UserVisibleError(Exception):
    pass


def get_diff_files(diffset, interdiffset=None):
    def get_original_file(file, revision):
        """Get a file either from the cache or the SCM.  SCM exceptions are
           passed back to the caller."""
        tool = diffset.repository.get_scmtool()

        try:
            if revision == scmtools.HEAD:
                return tool.get_file(file, revision)
            else:
                return cache_memoize("%s-%s" % (file, revision),
                    lambda: tool.get_file(file, revision))
        except Exception, e:
            raise UserVisibleError(str(e))

    def get_patched_file(buffer, filediff):
        try:
            return diffutils.patch(filediff.diff, buffer, filediff.dest_file)
        except Exception, e:
            raise UserVisibleError(str(e))


    def get_chunks(filediff, interfilediff=None):
        def diff_line(linenum, oldline, newline):
            if not oldline or not newline:
                return [linenum, oldline or '', [], newline or '', []]

            oldregion, newregion = \
                diffutils.get_line_changed_regions(oldline, newline)

            return [linenum, oldline, oldregion, newline, newregion]

        def new_chunk(lines, numlines, tag, collapsable=False):
            return {
                'lines': lines,
                'numlines': numlines,
                'change': tag,
                'collapsable': collapsable,
            }

        def add_ranged_chunks(lines, start, end, collapsable=False):
            numlines = end - start
            chunks.append(new_chunk(lines[start:end], end - start, 'equal',
                          collapsable))

        file = filediff.source_file
        revision = filediff.source_revision

        if revision == scmtools.PRE_CREATION:
            old = ""
        else:
            old = get_original_file(file, revision)

        new = get_patched_file(old, filediff)

        if interfilediff:
            old, new = new, get_patched_file(old, interfilediff)

        a = (old or '').splitlines()
        b = (new or '').splitlines()
        a_num_lines = len(a)
        b_num_lines = len(b)

        chunks = []
        linenum = 1
        differ = diffutils.Differ(a, b, ignore_space=True,
                                  compat_version=diffset.diffcompat)

        for tag, i1, i2, j1, j2 in differ.get_opcodes():
            oldlines = a[i1:i2]
            newlines = b[j1:j2]
            numlines = max(len(oldlines), len(newlines))
            lines = map(diff_line,
                        range(linenum, linenum + numlines), oldlines, newlines)
            linenum += numlines

            if tag == 'equal' and \
               numlines >= settings.DIFF_CONTEXT_COLLAPSE_THRESHOLD:
                last_range_start = numlines - settings.DIFF_CONTEXT_NUM_LINES

                if len(chunks) == 0:
                    add_ranged_chunks(lines, 0, last_range_start, True)
                    add_ranged_chunks(lines, last_range_start, numlines)
                else:
                    add_ranged_chunks(lines, 0, settings.DIFF_CONTEXT_NUM_LINES)

                    if i2 == a_num_lines and j2 == b_num_lines:
                        add_ranged_chunks(lines,
                                          settings.DIFF_CONTEXT_NUM_LINES,
                                          numlines, True)
                    else:
                        add_ranged_chunks(lines,
                                          settings.DIFF_CONTEXT_NUM_LINES,
                                          last_range_start, True)
                        add_ranged_chunks(lines, last_range_start, numlines)
            else:
                chunks.append(new_chunk(lines, numlines, tag))

        return chunks

    def add_navigation_cues(files):
        """Add index, nextid and previd data to a list of files/chunks"""
        # FIXME: this modifies in-place right now, which is kind of ugly
        interesting = []
        indices = []
        for i, file in enumerate(files):
            file['index'] = i
            k = 1
            for j, chunk in enumerate(file['chunks']):
                if chunk['change'] != 'equal':
                    interesting.append(chunk)
                    indices.append((i, k))
                    k += 1

            file['num_changes'] = k - 1

        for chunk, previous, current, next in zip(interesting,
                                                  [None] + indices[:-1],
                                                  indices,
                                                  indices[1:] + [None]):
            chunk['index'] = current[1]
            if previous:
                chunk['previd'] = '%d.%d' % previous
            if next:
                chunk['nextid'] = '%d.%d' % next


    files = []
    for filediff in diffset.files.all():
        if filediff.binary:
            chunks = []
        elif interdiffset:
            # XXX This is slow. We should optimize this.
            interfilediff = None
            for filediff2 in interdiffset.files.all():
                if filediff2.source_file == filediff.source_file:
                    interfilediff = filediff2
                    break

            if interfilediff:
                chunks = cache_memoize('diff-sidebyside-interdiff-%s-%s' %
                                       (filediff.id, interfilediff.id),
                                       lambda: get_chunks(filediff,
                                                          interfilediff))
        else:
            chunks = cache_memoize('diff-sidebyside-%s' % filediff.id,
                                   lambda: get_chunks(filediff))

        revision = filediff.source_revision

        if revision == scmtools.HEAD:
            revision = "HEAD"
        elif revision == scmtools.PRE_CREATION:
            revision = "Pre-creation"
        else:
            revision = "Revision %s" % revision

        files.append({
            'depot_filename': filediff.source_file,
            'revision': revision,
            'chunks': chunks,
            'filediff': filediff,
            'binary': filediff.binary,
        })

    add_navigation_cues(files)

    return files


def view_diff(request, diffset_id, interdiffset_id=None, extra_context={},
              template_name='diffviewer/view_diff.html'):
    diffset = get_object_or_404(DiffSet, pk=diffset_id)

    if interdiffset_id:
        interdiffset = get_object_or_404(DiffSet, pk=interdiffset_id)
    else:
        interdiffset = None

    try:
        files = get_diff_files(diffset, interdiffset)

        if request.GET.get('expand', False):
            collapseall = False
        elif request.GET.get('collapse', False):
            collapseall = True
        elif request.COOKIES.has_key('collapsediffs'):
            collapseall = (request.COOKIES['collapsediffs'] == "True")
        else:
            collapseall = True

        context = {
            'diffset': diffset,
            'interdiffset': interdiffset,
            'files': files,
            'collapseall': collapseall,
        }
        context.update(extra_context)

        response = render_to_response(template_name,
                                      RequestContext(request, context))

        response.set_cookie('collapsediffs', collapseall)

        return response

    except Exception, e:
        context = { 'error': e, }
        if e.__class__ is not UserVisibleError:
            context['trace'] = traceback.format_exc()

        return render_to_response(template_name,
                                  RequestContext(request, context))


def view_diff_fragment(request, diffset_id, filediff_id,
                       template_name='diffviewer/diff_file_fragment.html'):
    diffset = get_object_or_404(DiffSet, pk=diffset_id)
    filediff = get_object_or_404(FileDiff, pk=filediff_id, diffset=diffset)

    try:
        files = get_diff_files(filediff.diffset)

        for file in files:
            if file['filediff'].id == filediff.id:
                return render_to_response(template_name,
                    RequestContext(request, {
                        'file': file,
                        'standalone': True,
                    })
                )

        raise UserVisibleError(
            "Internal error. Unable to locate file record for filediff %s" % \
            filediff.id)
    except Exception, e:
        context = { 'error': e, 'standalone': True, }
        if e.__class__ is not UserVisibleError:
            context['trace'] = traceback.format_exc()

        return render_to_response(template_name,
                                  RequestContext(request, context))


def upload(request, donepath, diffset_history_id=None,
           template_name='diffviewer/upload.html'):
    differror = None
    repository_id = request.REQUEST.get('repositoryid', None)

    if repository_id == None:
        return HttpResponse("A repository ID was not specified")

    try:
        repository = Repository.objects.get(pk=repository_id)
    except Repository.DoesNotExist:
        return HttpResponse("Repository ID %s was invalid" % repository_id)

    if request.method == 'POST':
        form_data = request.POST.copy()
        form_data.update(request.FILES)
        form = UploadDiffForm(form_data)

        if form.is_valid():
            if diffset_history_id != None:
                diffset_history = get_object_or_404(DiffSetHistory,
                                                    pk=diffset_history_id)
            else:
                diffset_history = None

            try:
                diffset = form.create(request.FILES['path'], diffset_history)
                return HttpResponseRedirect(donepath % diffset.id)
            except scmtools.FileNotFoundException, e:
                differror = str(e)
            except ValueError:
                # FIXME: it'd be nice to have some help as to exactly what broke
                # during parsing.
                differror = 'This diff did not parse correctly'
    else:
        form = UploadDiffForm(initial={'repositoryid': repository_id})

    return render_to_response(template_name, RequestContext(request, {
        'differror': differror,
        'form': form,
        'diffs_use_absolute_paths':
            repository.get_scmtool().get_diffs_use_absolute_paths(),
    }))
