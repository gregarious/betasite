from django.shortcuts import get_object_or_404

from onlyinpgh.common.core.rendering import render_viewmodel, render_safe
from onlyinpgh.common.views import page_response, render_main

from onlyinpgh.events.models import Event
from onlyinpgh.events.viewmodels import EventFeedItem, EventDetail


def page_feed(request):
    '''
    View function that handles a page load request for a feed of place
    items.

    Returns page response with main content set to the feed.
    '''
    # get a list of rendered items
    events = Event.objects.all()[:10]
    items = [EventFeedItem(event, user=request.user) for event in events]

    rendered_items = [render_viewmodel(item, 'events/feed_item.html') for item in items]
    rendered_feed = render_safe('events/main_feed.html', items=rendered_items)
    main = render_main(rendered_feed, include_scenenav=True)
    return page_response(main, request)


def page_details(request, eid):
    '''
    Returns page response with main content set to the details.
    '''
    # build and render event detail viewmodel
    event = get_object_or_404(Event, id=eid)
    details = EventDetail(event, user=request.user)
    content = render_viewmodel(details,
                template='events/single.html',
                class_label='event-single')
    main = render_main(content, include_scenenav=False)
    return page_response(main, request)


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
