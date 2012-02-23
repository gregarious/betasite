from django.shortcuts import render_to_response
from django.db.models import Q

from datetime import datetime

from onlyinpgh.places.models import Place, Meta as PlaceMeta
from onlyinpgh.events.models import Event
from onlyinpgh.news.models import Article
from onlyinpgh.offers.models import Offer

from onlyinpgh.utils.jsontools import jsonp_response

def hot_page(request):
    variables = { 'places': Place.objects.all(), 'events': Event.objects.all(), 'news': Article.objects.all(), 'offers': Offer.objects.all() }
    return render_to_response('hot.html',variables)

def map_page(request):
	variables = { 'places': Place.objects.all(), 'events': Event.objects.all(), 'news': Article.objects.all(), 'offers': Offer.objects.all() }
	return render_to_response('map.html',variables)	

# Empty template for splash and search pages
def checkin_page(request):
	variables = {}
	return render_to_response('grabbit.html',variables)	

def search_page(request):
	variables = {}
	return render_to_response('search.html',variables)		

### OBID views ###
@jsonp_response
def ajax_hot_page(request):
    data = {'events':   [],
            'specials': [],
            'places':   [],
            'news':     [],
            }

    for e in Event.objects.filter(dtstart__gt=datetime.utcnow()).order_by('dtstart')[:3]:
        d = e.dtstart.strftime('%b ') + e.dtstart.strftime('%d').lstrip('0')
        t = e.dtstart.strftime('%I:').lstrip('0') + e.dtstart.strftime('%M %p')
        data['events'].append( {'name':e.name, 
                                'start_date':d,
                                'start_time':t,
                                'image_url':e.image_url} )
    
    # filter just for show
    for p in Place.objects.filter(~Q(location__address='')).order_by('?')[:3]:
        data['places'].append( {'name':p.name,'address':p.location.address, 'id':p.id} )
    
    for o in Offer.objects.all()[:3]:
        data['specials'].append( {'stub':o.description, 'points':o.point_value} )
    
    for a in Article.objects.all():
        data['news'].append( {'title':a.title, 'source':source_name} )

    return data