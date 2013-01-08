from django.shortcuts import get_object_or_404, render_to_response

from django.utils import timezone
import datetime

from scenable.common.views import PageContext, FeedView
from scenable.common.forms import CategorySearchForm

from scenable.events.models import Event, Category
from scenable.events.viewmodels import EventData

from haystack.query import SearchQuerySet


class PageEventsFeed(FeedView):
    '''
    Class-based view that shows main feed of events
    '''
    def __init__(self):
        # used to render the page with correctly configured PageContext
        context_factory = lambda request: \
            PageContext(request,
                current_section='events',
                page_title='Scenable | Oakland Events')

        # set static attributes of the view class here
        super(PageEventsFeed, self).__init__(
            template='events/page_feed.html',
            page_context_factory=context_factory,
            viewmodel_class=EventData,
            results_per_page=8)

    def build_search_form(self, data=None):
        '''
        Returns a form for that will search all Events with an event category
        dropdown.
        '''
        category_choices = [(str(cat.id), cat.label)
            for cat in Category.objects.order_by('id')]
        category_choices.insert(0, ('0', 'All Events'))

        # Haystack (or elasticsearch?) stores all times as naive datetimes in UTC
        sqs = SearchQuerySet().models(Event) \
                    .filter(dtend__gt=datetime.datetime.now()) \
                    .order_by('dtend')

        return CategorySearchForm(choices=category_choices,
            searchqueryset=sqs,
            data=data)

    def get_all_results(self):
        '''
        Returns all events, sorted by end time.
        '''
        return Event.listed_objects \
                    .filter(dtend__gt=timezone.now()) \
                    .order_by('dtend')

    def apply_category_filter(self, category_key, results):
        '''
        Only include results with the given category_key.
        '''
        # Don't filter if no category, or if category is '0' (this key refers
        # to "All Results").
        if not category_key or category_key == '0':
            return results

        # otherwise, apply and include filter for results that have the category
        contains_category = lambda obj: category_key in [str(cat.id) for cat in obj.categories.all()]
        return [result for result in results if contains_category(result)]


def page_details(request, eid):
    '''
    Returns page response with main content set as:
        event (EventContext object)
    '''
    event = get_object_or_404(Event, id=eid)
    details = EventData(event, user=request.user)

    content = {'event': details}
    page_context = PageContext(request,
        current_section='events',
        page_title='Scenable | %s' % event.name,
        content_dict=content)

    return render_to_response('events/page_event.html', context_instance=page_context)
