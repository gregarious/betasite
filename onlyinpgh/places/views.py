from django.http import HttpResponse
from django.shortcuts import render_to_response
from onlyinpgh.places.models import Place, Meta as PlaceMeta

from onlyinpgh.utils.decorators import jsonp_response
from onlyinpgh.utils import ViewInstance, get_or_none

class ViewPlace(ViewInstance):
    def __init__(self,place):
        super(ViewPlace,self).__init__(place,extract_m2m=True)
        def get_meta(key):
            meta = get_or_none(place.meta_set,meta_key=key)
            return meta.meta_value if meta else None

        self.phone = get_meta('phone')
        self.url = get_meta('url')
        self.hours = get_meta('hours')
        self.image_url = get_meta('image_url')

    def to_app_data(self):
        tags = [tagitem.tag for tagitem in self.tags]
        tag_data = [{'name':t.name,'id':t.id} for t in tags]
        data = {
            'id':       self.id,
            'name':     self.name,
            'description':  self.description,
            'image_url':    self.image_url,
            'tags': tag_data,
            'hours':    self.hours,
            'url':      self.url,
        }

        if self.location:
            data['location'] = {
                    'address':      self.location.address,
                    'longitude':    float(self.location.longitude),
                    'latitude':     float(self.location.latitude),
                },
        return data

def _view_data_all():
    return [ViewPlace(p) for p in Place.objects.select_related().all()][:10]

def _view_data_id(pid):
    return ViewPlace(Place.objects.select_related().get(id=pid))

def feed_page(request):
    data = {'places':   _view_data_all()}
    return render_to_response('place/feed.html',data)

def detail_page(request,pid):
    data = {'places':   _view_data_id(pid)}
    return render_to_response('place/single.html',data)

@jsonp_response
def feed_app(request):
    data = {'places':   [vp.to_app_data() for vp in _view_data_all()]}
    return data

@jsonp_response
def detail_app(request,pid):
    data = {'place':    _view_data_id(pid).to_app_data()}
    return data
