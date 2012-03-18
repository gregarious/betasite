from django.http import HttpResponse
from django.template.loader import render_to_string
from django.template import RequestContext
from django.utils.safestring import mark_safe


def render_admin_page(safe_content, context_instance=None):
    '''
    Renders a page in the admin interface.
    '''
    content = {
        'content': mark_safe(safe_content)
    }
    return render_to_string('orgadmin/base.html',
        content, context_instance=context_instance)


def response_admin_page(safe_content, context_instance=None):
    return HttpResponse(render_admin_page(safe_content, context_instance))


def page_signup(request):
    return response_admin_page('signup', RequestContext(request))


def page_login(request):
    return response_admin_page('login', RequestContext(request))


def page_home(request):
    return response_admin_page('home', RequestContext(request))
