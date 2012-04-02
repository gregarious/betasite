'''
Script to flesh out existing place objects with Facebook page information.

Note this is a new (March 2012) script to be used with new style Places
'''

from onlyinpgh.places.models import Place, PlaceMeta
from onlyinpgh.places.outsourcing import facebook
from onlyinpgh.outsourcing.apitools.facebook import FacebookAPIError


def run():
    places = Place.objects.exclude(fb_id='')
    for place in places:
        if PlaceMeta.objects.filter(place=place, key='debug_fb_linked').count() == 0:
            print 'updating', place, '(fb id %s)' % str(place.fb_id)
            try:
                facebook.complete_place_data(place, save=True)
            except FacebookAPIError as e:
                print 'Facebook API error:', e
                continue
            # uncomment to avoid waiting on already pulled pages during debugging
            # PlaceMeta.objects.get_or_create(place=place, key='debug_fb_linked')
        else:
            print 'skipping', place, '(fb id %s)' % str(place.fb_id)
