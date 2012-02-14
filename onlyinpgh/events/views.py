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
        if e.dtend.strftime('%d') == e.dtstart.strftime('%d'):
            dtend_str = e.dtend.strftime('%H:%M')
        else:
            dtend_str = e.dtend.strftime('%Y-%m-%d %H:%M')
        
        events.append({
            'name': e.name,
            'dtstart': e.dtstart.strftime('%Y-%m-%d %H:%M'),
            'dtend': dtend_str,
            'id': e.id})

    return {'events':events}    # decorator will handle JSONP details and HTTP response

@jsonp_response
def ajax_event_item(request,eid):
    e = Event.objects.get(id=eid)
    event_data = {  'name':e.name,
                    'dtstart':e.dtstart.strftime('%Y-%m-%d %H:%M') }
    return {'event':event_data}