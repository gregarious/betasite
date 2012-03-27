from django import template
from onlyinpgh.common.core.rendering import render_viewmodel


def vmrender(viewmodel, template):
    print type(viewmodel), viewmodel, template
    return render_viewmodel(viewmodel, template)


register = template.Library()
register.simple_tag(vmrender)
