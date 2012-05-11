from django.http import HttpResponseForbidden
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required

# from onlyinpgh.common.utils.jsontools import serialize_resources, jsonp_response, sanitize_json
from onlyinpgh.common.views import PageContext, PageFilteredFeed

from onlyinpgh.specials.models import Special, Coupon
from onlyinpgh.specials.viewmodels import SpecialData
# from onlyinpgh.specials.resources import SpecialFeedResource

from haystack.forms import SearchForm
from django.utils import timezone


class PageSpecialsFeed(PageFilteredFeed):
    def __init__(self, *args, **kwargs):
        super(PageSpecialsFeed, self).__init__(
            model_class=Special,
            viewmodel_class=SpecialData,
            template='specials/page_feed.html',
            form_class=SearchForm,
            results_per_page=6,
        )

    def get_page_context(self, content):
        return PageContext(self.request,
            current_section='specials',
            page_title='Scenable | Oakland Specials',
            content_dict=content)

    def hacked_unfiltered(self):
        return Special.objects.filter(dexpires__gt=timezone.now()).order_by('dexpires')

    def hacked_filtered(self):
        return sorted([result.object for result in self.form.search()
                        if result.object.dexpires > timezone.now()],
                        key=lambda s: s.dexpires)


@login_required
def page_details(request, sid):
    '''
    View displays single specials.
    '''
    # build and render special detail viewmodel
    special = get_object_or_404(Special, id=sid)
    details = SpecialData(special, user=request.user)
    content = {'special': details}
    page_context = PageContext(request,
        current_section='specials',
        page_title='Scenable | %s' % special.title,
        content_dict=content)

    return render_to_response('specials/page_special.html', context_instance=page_context)


def page_coupon(request, uuid):
    coupon = get_object_or_404(Coupon, uuid=uuid)
    content = {
        'coupon': coupon,
        'print': request.GET.get('print')
    }
    context = RequestContext(request)
    if coupon.was_used:
        # TODO: redirect to some error page?
        return HttpResponseForbidden()
    else:
        return render_to_response('specials/page_coupon.html', content, context_instance=context)
