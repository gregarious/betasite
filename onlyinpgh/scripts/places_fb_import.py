'''
Script to flesh out existing place objects with Facebook page information.

Note this is a new (March 2012) script to be used with new style Places
'''

from onlyinpgh.places.models import Place, PlaceMeta
from onlyinpgh.places.outsourcing import facebook
from onlyinpgh.outsourcing.apitools.facebook import FacebookAPIError

import datetime
from django.db import transaction


@transaction.commit_on_success
def commit_place(place):
    fields_changed = facebook.supplement_place_data(place)

    # if some fields were changed, track it
    if len(fields_changed) > 0:
        print 'fields changed:', fields_changed
        for field in fields_changed:
            PlaceMeta.objects.get_or_create(place=place,
                                            key='fb_synced_field',
                                            value=field)
        # set the last synced time to now
        try:
            last_synced = PlaceMeta.objects.get(place=place, key='fb_last_synced')
        except PlaceMeta.DoesNotExist:
            PlaceMeta.objects.create(place=place, key='fb_last_synced',
                                        value=datetime.datetime.now().isoformat())
        else:
            last_synced.value = datetime.datetime.now().isoformat()
            last_synced.save()
    else:
        print 'nothing changed'


def run():
    places = Place.objects.exclude(fb_id='')
    for place in places:
        if PlaceMeta.objects.filter(place=place, key='debug_fb_linked').count() == 0:
            print 'updating', place, '(fb id %s)' % str(place.fb_id)
            try:
                commit_place(place)
            except FacebookAPIError as e:
                print 'Facebook API error:', e
            except IOError as e:
                print e
            # uncomment to avoid waiting on already pulled pages during debugging
            # PlaceMeta.objects.get_or_create(place=place, key='debug_fb_linked')
        else:
            print 'skipping', place, '(fb id %s)' % str(place.fb_id)
