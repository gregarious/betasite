from django.http import HttpResponseForbidden
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required

from scenable.common.views import PageContext, PageFilterableFeed

from scenable.specials.models import Special, Coupon
from scenable.specials.viewmodels import SpecialData

from haystack.query import SearchQuerySet
from django.utils.timezone import now


class PageSpecialsFeed(PageFilterableFeed):
    def __init__(self, *args, **kwargs):
        sqs = SearchQuerySet().models(Special).order_by('dexpires')
        qs = Special.objects.order_by('dexpires')
        super(PageSpecialsFeed, self).__init__(
            template='specials/page_feed.html',
            searchqueryset=sqs,
            nosearch_queryset=qs,
            categories=[],  # disabled for now
            viewmodel_class=SpecialData,
            results_per_page=8,
        )

    def get_results(self):
        '''
        Due to a problem with Haystack/Elasticsearch filtering on nullable
        fields (not sure which one), the filtering by expiration date must
        be done manually after the search.
        '''
        results = super(PageSpecialsFeed, self).get_results()

        if self.search_used:
            # go through result.objects
            return [result for result in results
                        if result.object.dexpires is None or \
                           result.object.dexpires >= now().date()]
        else:
            # go through bare results
            return [result for result in results
                        if result.dexpires is None or result.dexpires >= now().date()]

    def get_page_context(self, request):
        '''
        Return a dict of extra context variables. Override this.
        '''
        return PageContext(self.request,
            current_section='specials',
            page_title='Scenable | Oakland Specials')


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
