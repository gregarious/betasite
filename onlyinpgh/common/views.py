from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.shortcuts import render_to_response


### UTILITY FUNCTIONS ###
def render_topbar(user):
    topbar_content = render_to_string('top_bar.html', {'user': user})
    return mark_safe(topbar_content)


def render_footer():
    footer_content = render_to_string('footer.html')
    return mark_safe(footer_content)


def render_sidebar():
    sidebar_content = render_to_string('sidebar.html')
    return mark_safe(sidebar_content)


def render_scenenav():
    scenenav_content = render_to_string('scene_nav.html')
    return mark_safe(scenenav_content)


def render_main(rendered_content, include_scenenav=False):
    '''
    Returns rendered HTML with the main site content wrapped in
    main_nav.html or main_nonav.html (depending on the state of
    include_scenenav)
    '''
    content_dict = {
        'content': rendered_content,
    }
    if include_scenenav:
        content_dict['scene_nav'] = render_scenenav()
        return render_to_string('main_nav.html', content_dict)
    else:
        return render_to_string('main.html', content_dict)


def page_response(main_content, request=None, topbar_content=None,
                    sidebar_content=None, footer_content=None):
    '''
    Responds with an HttpResponse of a fully rendered page.

    main_content must be explicitly laid out, while the other content
    variables will be automatically generated as follows:
    - topbar_content: rendered with top_bar.html (user: request.user)
    - sidebar_content: rendered with sidebar.html
    - footer_content: rendered with footer.html
    '''
    if not topbar_content:
        topbar_content = render_topbar(request.user) if request else render_topbar()
    if not sidebar_content:
        sidebar_content = render_sidebar()
    if not footer_content:
        footer_content = render_footer()

    content_dict = {
        'topbar': topbar_content,
        'main': main_content,
        'sidebar': sidebar_content,
        'footer': footer_content,
    }

    return render_to_response('page.html', content_dict)


### URL-LINKED VIEWS ###
def page_home(request):
    main_content = render_main('Home!')
    return page_response(main_content, request)
