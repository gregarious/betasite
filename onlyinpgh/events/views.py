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

def split_dt(dt):
    d = dt.strftime('%b ') + dt.strftime('%d').lstrip('0')
    t = dt.strftime('%I:').lstrip('0') + dt.strftime('%M %p')

    return(d,t)

@jsonp_response
def ajax_events_feed(request):
    events = []
    for e in Event.objects.filter(dtstart__gt=datetime.utcnow()).order_by('dtstart')[:10]:
        events.append({
            'id':   e.id,
            'name': e.name,
            'start_date': split_dt(e.dtstart)[0],
            'start_time': split_dt(e.dtstart)[1],
            'end_time': split_dt(e.dtend)[1],
            })

    return {'events':events}    # decorator will handle JSONP details and HTTP response

@jsonp_response
def ajax_event_item(request,eid):
    e = Event.objects.get(id=eid)
    event_data = {  'id':   e.id,
                    'name': e.name,
                    'start_date': split_dt(e.dtstart)[0],
                    'start_time': split_dt(e.dtstart)[1],
                    'end_time': split_dt(e.dtend)[1]}
    
    p = e.place
    if p:
        place = {'id':   p.id,
                'name': p.name}            
        loc = p.location
        if loc:
            place['address'] = loc.address
            place['latitude'] = float(loc.latitude) if loc.latitude else None
            place['longitude'] = float(loc.longitude) if loc.longitude else None
        event_data['place'] = place

    return {'event':event_data}