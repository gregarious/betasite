from django.shortcuts import render_to_response, redirect
from django.core.urlresolvers import reverse

from django.http import Http404


def render_page(template, page_context):
    return render_to_response(template, context_instance=page_context)


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
