from django.shortcuts import get_object_or_404, render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from onlyinpgh.common.utils.jsontools import serialize_resources, jsonp_response
from onlyinpgh.common.views import PageContext

from onlyinpgh.events.models import Event
from onlyinpgh.events.viewmodels import EventData
from onlyinpgh.events.resources import EventFeedResource


def page_feed(request):
    '''
    View function that handles a page load request for a feed of event
    items.

    Returns page response with main content set as:
        items: list of EventContext items
        prev_p: number of previous page events (if applicable)
        next_p: number of next page of events (if applicable)
    '''
    all_events = Event.listed_objects.all()
    paginator = Paginator(all_events, 10)
    page = request.GET.get('p')
    try:
        events = paginator.page(page)
    except PageNotAnInteger:
        events = paginator.page(1)
    except EmptyPage:
        events = paginator.page(paginator.num_pages)

    items = [EventData(event, user=request.user) for event in events]
    # need the items in json form for bootstrapping to BB models
    items_json = serialize_resources(EventFeedResource(), events, request=request)

    content = {'items': items,
               'items_json': items_json,
               'prev_p': page.previous_page_number() if page.has_previous() else None,
               'next_p': page.next_page_number() if page.has_next() else None}

    page_context = PageContext(request,
        current_section='events',
        page_title='Scenable | Oakland Events',
        content_dict=content)
    return render_to_response('events/page_feed.html', page_context)


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

    return render_to_response('events/page_event.html', page_context)

# from django.shortcuts import render_to_response
# from django.template import Context, RequestContext
# from django.template.loader import get_template

# from onlyinpgh.events.models import Event, Attendee
# from onlyinpgh.common.utils.jsontools import jsonp_response

# class FeedItem(object):
#     pass
# #from onlyinpgh.common.rendering import FeedItem

# from datetime import datetime

# class EventFeedItem(FeedItem):
#     template_name = 'events/feed_item.html'
#     dom_class = 'events_feed'
#     def __init__(self,event,user=None):
#         self.event = event

#         if user:
#             self.is_attending = Attendee.objects.filter(user=user,event=event)\
#                                                 .count() > 0

#     @classmethod
#     def render_feed_from_events(cls,events,request=None):
#         user = request.user if request else None
#         items = [cls(event,user) for event in events]
#         blocks = [item.self_render() for item in items]
#         return cls.render_feed_from_blocks(blocks,dom_class='events_feed',request=request)

#     def to_app_data(self):
#         data = { 'event': {
#                     'id':   e.id,
#                     'name': e.name,
#                     'start_date': split_dt(e.dtstart)[0],
#                     'start_time': split_dt(e.dtstart)[1],
#                     'end_time': split_dt(e.dtend)[1]
#                     },
#                 }
#         return data

# class SingleItem(FeedItem):
#     pass

# # def events_page(request):
# #     variables = { 'events': Event.objects.filter(invisible=False) }
# #     return render_to_response('events/events_page.html',variables)

# # def single_event_page(request, id):
# #     variables = { 'e' : Event.objects.get(id=id) }
# #     return render_to_response('events/events_single.html', variables)

# def _split_dt(dt):
#     d = dt.strftime('%b ') + dt.strftime('%d').lstrip('0')
#     t = dt.strftime('%I:').lstrip('0') + dt.strftime('%M %p')

#     return(d,t)

# @jsonp_response
# def ajax_events_feed(request):
#     events = []
#     for e in Event.objects.filter(dtstart__gt=datetime.utcnow()).order_by('dtstart')[:10]:
#         events.append({
#             'id':   e.id,
#             'name': e.name,
#             'start_date': split_dt(e.dtstart)[0],
#             'start_time': split_dt(e.dtstart)[1],
#             'end_time': split_dt(e.dtend)[1],
#             })

#     return {'events':events}    # decorator will handle JSONP details and HTTP response

# @jsonp_response
# def ajax_event_item(request,eid):
#     e = Event.objects.get(id=eid)
#     event_data = {  'id':   e.id,
#                     'name': e.name,
#                     'start_date': split_dt(e.dtstart)[0],
#                     'start_time': split_dt(e.dtstart)[1],
#                     'end_time': split_dt(e.dtend)[1]}

#     p = e.place
#     if p:
#         place = {'id':   p.id,
#                 'name': p.name}
#         loc = p.location
#         if loc:
#             place['address'] = loc.address
#             place['latitude'] = float(loc.latitude) if loc.latitude else None
#             place['longitude'] = float(loc.longitude) if loc.longitude else None
#         event_data['place'] = place

#     return {'event':event_data}

#     ###### TEST ERASE #####
# from django.http import HttpResponse
# from django import forms
# from django.template import Template

# page_template = Template('''
# <form action="#" method="post">
# {% csrf_token %}
# {% for field in form %}
#     <div class="fieldWrapper">
#         {{ field.errors }}
#         {{ field.label_tag }}: {{ field }}
#     </div>
# {% endfor %}
# <input type="submit" value="Submit" />
# </form>
# ''')

# from django.contrib.auth.models import User
# from onlyinpgh.organizations.models import Organization
# class EventForm(forms.ModelForm):
#     class Meta:
#         model = Organization


# def formtest(request):
#     if request.POST:
#         form = EventForm(request.POST)
#         #if form.is_valid():
#         #return HttpResponse('place saved!')
#     else:
#         form = EventForm()

#     context = RequestContext(request, {'form': form})
#     return HttpResponse(page_template.render(context))
