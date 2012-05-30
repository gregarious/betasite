from django import template
from scenable.common.core.rendering import render_viewmodel
from scenable.common.utils import process_external_url
from django.template.defaultfilters import stringfilter
from django.core.urlresolvers import reverse
import urllib

register = template.Library()


@register.filter
@stringfilter
def external_url(url):
    return process_external_url(url)


def feed_urlencode(viewname, page_num=None, q=None):
    url = reverse(viewname)
    queryargs = {}
    if page_num != '' and page_num is not None:
        queryargs['page'] = page_num
    if q != '' and q is not None:
        queryargs['q'] = q

    if queryargs:
        return url + '?' + urllib.urlencode(queryargs)
    else:
        return url


def vmrender(viewmodel, template):
    return render_viewmodel(viewmodel, template)


register.simple_tag(vmrender)
register.simple_tag(feed_urlencode)
