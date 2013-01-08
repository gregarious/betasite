from django.http import HttpResponseForbidden
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response

from scenable.common.views import PageContext, FeedView

from scenable.specials.models import Special, Coupon
from scenable.specials.viewmodels import SpecialData

from haystack.query import SearchQuerySet
from haystack.forms import SearchForm

from django.utils import timezone
import datetime


class PageSpecialsFeed(FeedView):
    '''
    Class-based view that shows main feed of specials
    '''
    def __init__(self):
        # used to render the page with correctly configured PageContext
        context_factory = lambda request: \
            PageContext(request,
                current_section='specials',
                page_title='Scenable | Oakland Specials')

        # set static attributes of the view class here
        super(PageSpecialsFeed, self).__init__(
            template='events/page_feed.html',
            page_context_factory=context_factory,
            viewmodel_class=SpecialData,
            results_per_page=8)

    def build_search_form(self, data=None):
        '''
        Returns a form for that will search all Events with an event category
        dropdown.
        '''
        # Haystack (or elasticsearch?) stores all times as naive datetimes in UTC
        sqs = SearchQuerySet().models(Special) \
            .filter(dexpires__gte=datetime.datetime.now().date()) \
            .order_by('dexpires')

        return SearchForm(searchqueryset=sqs, data=data)

    def get_all_results(self):
        '''
        Returns all events, sorted by end time.
        '''
        return Special.objects.order_by('dexpires') \
            .filter(dexpires__gte=timezone.now()) \
            .order_by('dexpires')


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
