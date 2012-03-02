from onlyinpgh.common.core.viewmodels import ViewModel, RenderableViewModel

from onlyinpgh.common.viewmodels import FeedViewModel
from onlyinpgh.tags.viewmodels import TagList
from onlyinpgh.identity.models import FavoriteItem

def to_directions_link(location):
    daddr = ''
    if location.address:
        daddr = location.address
        if location.postcode:
            daddr += ', ' + location.postcode
    elif location.longitude and not location.latutude:
        daddr = '(%f,%f)' % (float(location.longitude),float(location.latutude))

    if not daddr:
        return None
    else:
        return 'http://maps.google.com/maps?' + urllib.urlencode({'daddr':daddr})

def location_to_data(location):
    '''Helper for ViewModels that need a subset of Location data'''
    return {
        'address':      location.address,
        'longitude':    float(location.longitude) if location.longitude else None,
        'latitude':     float(location.latitude) if location.latitude else None,
    }

def place_to_data(place,place_meta):
    '''Helper for ViewModels that need a subset of Place data'''
    data = {    
        'id':       place.id,
        'name':     place.name,
        'description':     place.description,
        'location': location_to_data(place.location) if place.location else None,
    }
    data.update(place_meta)
    return data

class PlaceFeedItem(RenderableViewModel):
    template_name = 'places/feed_item.html'
    
    def __init__(self,place,user=None):
        self._place = place
        # FeedItems only need the image_url
        self._meta = {
            'image_url': place.get_meta('image_url')
        }
        # temporary placeholder
        if not self._meta['image_url']:
            self._meta['image_url'] = '/static/img/default_place.png'

        self.tag_list = TagList(place.tags.all())
        if user:
            self.is_favorite = FavoriteItem.objects.filter_by_type(model_instance=place).count() > 0
            
    def to_data(self,*args,**kwargs):
        '''Manually handles setting of place data'''
        cleaned_dict = super(PlaceFeedItem,self).to_data(*args,**kwargs)
        cleaned_dict['place'] = place_to_data(self._place,self._meta)
        return cleaned_dict

class PlacesFeed(FeedViewModel):
    class_name = 'places'

    @classmethod
    def init_from_places(cls,places,user=None):
        '''
        Factory constructor to initiate a feed from a list of Places.
        '''
        inst = cls()
        inst.items = [PlaceFeedItem(p) for p in places]
        return inst

class PlaceDetail(RenderableViewModel):
    template_name = 'places/single.html'

    def __init__(self,place,user=None):
        self._place = place
        self._meta = { key: place.get_meta(key) for key in 
                        ('image_url','hours','phone','url') }

        # temporary placeholder
        if not self._meta['image_url']:
            self._meta['image_url'] = 'http://www.nasm.si.edu/images/collections/media/thumbnails/DefaultThumbnail.gif'

        self.tag_list = TagList(place.tags.all())
        if user:
            self.is_favorite = FavoriteItem.objects.filter_by_type(model_instance=place).count() > 0

    def to_data(self,*args,**kwargs):
        '''Manually handles setting of place data'''
        cleaned_dict = super(PlaceDetail,self).to_data(*args,**kwargs)
        cleaned_dict['place'] = place_to_data(self._place,self._meta)
        return cleaned_dict


# class RelatedFeeds(SelfRenderingView):
#     template_name = 'feed_collection.html'

#     def __init__(self,place,user=None):
#         event_items = EventFeedItem.render_feed_from_events(
#                         Event.objects.filter(place=place),
#                         user)
#         #offer_items = offer_views.generate_feed(Offer.objects.filter(place=place))
        
#         self.feeds = [
#             {'label': 'events', 
#              'content': event_items },
#             {'label': 'offers', 
#              'content': 'More to come...' },
#             ]

#     def to_app_data(self):
#         return {}