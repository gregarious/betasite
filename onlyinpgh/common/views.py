from django.shortcuts import redirect, render_to_response
from django.core.urlresolvers import reverse

from django.http import Http404
from django.template import RequestContext


class PageContext(RequestContext):
    '''
    Used for main context variable for every main site page.
    '''
    def __init__(self, request, current_section=None, page_title=None, content_dict={}, **kwargs):
        '''
        current_section: string among 'places', 'events', 'news', etc...
        content_dict: context variables for main_context
        '''
        if page_title is None:
            page_title = "Scenable: You are a Beautiful Flower"

        variables = dict(
            page_title=page_title,
            current_section=current_section,
        )
        variables.update(content_dict)
        super(PageContext, self).__init__(request, variables, **kwargs)


def qr_redirect(request, key=None):
    if key is None:
        key = request.GET.get('id')

    if key == 'oakland':
        return redirect('oakland-teaser')
    elif key == 'shirt':
        return redirect('mobile-about')
    elif key == 'card':
        return redirect('mobile-about')
    else:
        print 'not found', key
        raise Http404


### URL-LINKED VIEWS ###
def page_home(request):
    return redirect(reverse('now'))


### STATIC PAGES ###
def page_static_about_oakland(request):
    context = PageContext(request, page_title="Scenable | About Oakland")
    return render_to_response('static_pages/about_oakland.html', context_instance=context)

def page_static_team(request):
    context = PageContext(request, page_title="Scenable | The Team")
    return render_to_response('static_pages/team.html', context_instance=context)

def page_static_mission(request):
    context = PageContext(request, page_title="Scenable | Our Mission")
    return render_to_response('static_pages/mission.html', context_instance=context)
