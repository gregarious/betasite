from django.shortcuts import render_to_response
from onlyinpgh.events.models import Event
from onlyinpgh.utils.decorators import jsonp_response

from datetime import datetime

def events_page(request):
    variables = { 'events': Event.objects.filter(invisible=False) }
    return render_to_response('events/events_page.html',variables)

def single_event_page(request, id):
    variables = { 'e' : Event.objects.get(id=id) }
    return render_to_response('events/events_single.html', variables)
    
@jsonp_response
def ajax_events_feed(request):
    events = []
    for e in Event.objects.filter(dtstart__gt=datetime.utcnow()).order_by('dtstart')[:10]:
        events.append({
            'name': e.name,
            'dtstart': e.dtstart.strftime('%Y-%m-%d %H:%I'),
            'dtend': e.dtend.strftime('%Y-%m-%d %H:%I')})
    return {'events':events}    # decorator will handle JSONP details
