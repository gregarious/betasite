from django.contrib.sites.models import get_current_site
from haystack.forms import SearchForm
from scenable.feedback.forms import GenericFeedbackForm


def site_domain(request):
    return {'site_domain': get_current_site(request).domain}


def site_search_form(request):
    return {'site_search_form': SearchForm()}


def sidebar_feedback_form(request):
    return {'sidebar_feedback_form': GenericFeedbackForm(user=request.user)}
