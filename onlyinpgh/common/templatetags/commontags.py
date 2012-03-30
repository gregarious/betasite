from django import template
from onlyinpgh.common.core.rendering import render_viewmodel
from onlyinpgh.common.utils import process_external_url
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def external_url(url):
    return process_external_url(url)


def vmrender(viewmodel, template):
    return render_viewmodel(viewmodel, template)


register.simple_tag(vmrender)
