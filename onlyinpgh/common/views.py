from django.shortcuts import render_to_response, redirect
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
        print 'redirecting to oakland'
        return redirect('splash')
    elif key == 'shirt':
        print 'redirecting to shirt'
        return redirect('splash')
    elif key == 'card':
        print 'redirecting to card'
        return redirect('splash')
    else:
        print 'not found', key
        raise Http404


### URL-LINKED VIEWS ###
def page_home(request):
    # this is a temporary hack -- should be in hot module but causes circular dependancy
    from onlyinpgh.hot.viewmodels import HotFeedCollection
    hot_feeds = HotFeedCollection(request.user)
    main_content = render_main(render_safe('hot.html', hot_feeds=hot_feeds))
    return page_response(main_content, request)

def example_chatter(request):
    return page_response(render_main(render_safe('chatter_example.html')),request)
def example_news(request):
    return page_response(render_main(render_safe('news_example.html')),request)

