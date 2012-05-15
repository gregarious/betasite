from django.shortcuts import get_object_or_404, render_to_response
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.utils import timezone

# from scenable.common.utils.jsontools import serialize_resources, jsonp_response, sanitize_json
from scenable.common.views import PageContext, PageFilteredFeed

from scenable.events.models import Event
from scenable.events.viewmodels import EventData
# from scenable.events.resources import EventFeedResource

from haystack.forms import SearchForm


class PageEventsFeed(PageFilteredFeed):
    def __init__(self, *args, **kwargs):
        super(PageEventsFeed, self).__init__(
            model_class=Event,
            viewmodel_class=EventData,
            template='events/page_feed.html',
            form_class=SearchForm,
            results_per_page=6,
        )

    def get_page_context(self, content):
        return PageContext(self.request,
            current_section='events',
            page_title='Scenable | Oakland Events',
            content_dict=content)

    def hacked_unfiltered(self):
        return Event.listed_objects.filter(dtend__gt=timezone.now()).order_by('dtstart')

    def hacked_filtered(self):
        # TODO: move this filtering into the query
        return sorted([result.object for result in self.form.search()
                        if result.object.dtend > timezone.now()],
                        key=lambda e: e.dtstart)


@login_required
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
