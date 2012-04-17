from django.shortcuts import render_to_response, redirect
from django.core.urlresolvers import reverse

from onlyinpgh.common.core.rendering import render_safe
from django.http import Http404


### UTILITY FUNCTIONS ###
def render_topbar(user):
    topbar_content = render_safe('top_bar.html', user=user)
    return topbar_content


def render_footer():
    return render_safe('footer.html')


def render_sidebar():
    return render_safe('sidebar_base.html')


def render_scenenav():
    return render_safe('scene_nav.html')


def render_main(rendered_content):
    '''
    Returns rendered HTML with the main site content wrapped in main.html
    '''
    return render_safe('main.html', content=rendered_content)


def render_page(template, page_context):
    return render_to_response(template, {'C': page_context})

def page_response(main_content, request=None, topbar_content=None,
                    scenenav_content=None, sidebar_content=None,
                    footer_content=None):
    '''
    Responds with an HttpResponse of a fully rendered page.

    main_content must be explicitly laid out, while the other content
    variables will be automatically generated as follows:
    - topbar_content: rendered with top_bar.html (user: request.user)
    - scenenav_content: rendered with scene_nav.html
    - sidebar_content: rendered with sidebar.html
    - footer_content: rendered with footer.html
    '''
    if not topbar_content:
        topbar_content = render_topbar(request.user) if request else render_topbar()
    if not scenenav_content:
        scenenav_content = render_scenenav()
    if not sidebar_content:
        sidebar_content = render_sidebar()
    if not footer_content:
        footer_content = render_footer()

    content_dict = {
        'topbar': topbar_content,
        'scenenav': scenenav_content,
        'main': main_content,
        'sidebar': sidebar_content,
        'footer': footer_content,
    }

    return render_to_response('page.html', content_dict)


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
    return redirect(reverse('hot'))


def example_chatter(request):
    raise NotImplementedError


def example_news(request):
    raise NotImplementedError
