from django import template
register = template.Library()


@register.simple_tag(takes_context=True)
def self_render(context, viewmodel):
    # if this statment throws a KeyError, first ensure that the request template
    # processor is listed in settings.py under TEMPLATE_CONTEXT_PROCESSORS
    # (see https://docs.djangoproject.com/en/dev/ref/templates/api/#django-core-context-processors-request)
    return viewmodel.to_html(request=context['request'])


@register.simple_tag
def self_render_nocontext(viewmodel):
    return viewmodel.to_html()
