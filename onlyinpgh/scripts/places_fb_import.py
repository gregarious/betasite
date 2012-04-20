'''
Script to flesh out existing place objects with Facebook page information.

Note this is a new (March 2012) script to be used with new style Places
'''

from onlyinpgh.places.models import Place, PlaceMeta
from onlyinpgh.places.outsourcing import facebook
from onlyinpgh.outsourcing.apitools.facebook import FacebookAPIError

from django.utils.timezone import now
from django.db import transaction

import logging
logging.root.setLevel(logging.INFO)


@transaction.commit_on_success
def commit_place(place, corporate=False):
    '''
    corporate=True for places whose FB pages are corporate and don't
    include local information.
    '''
    exclude_fields = ['phone', 'hours', 'parking', 'location'] if corporate else []
    fields_changed = facebook.supplement_place_data(place, exclude_fields=exclude_fields)

    # if some fields were changed, track it
    if len(fields_changed) > 0:
        logging.info('fields changed: %s', unicode(fields_changed))
        for field in fields_changed:
            PlaceMeta.objects.get_or_create(place=place,
                                            key='fb_synced_field',
                                            value=field)
        # set the last synced time to now
        try:
            last_synced = PlaceMeta.objects.get(place=place, key='fb_last_synced')
        except PlaceMeta.DoesNotExist:
            PlaceMeta.objects.create(place=place, key='fb_last_synced',
                                        value=now().isoformat())
        else:
            last_synced.value = now().isoformat()
            last_synced.save()


def run():
    places = Place.objects.exclude(fb_id='')
    for place in places:
        if PlaceMeta.objects.filter(place=place, key='debug_fb_linked').count() == 0:
            logging.info('updating', place, '(fb id %s)' % str(place.fb_id))
            try:
                commit_place(place)
            except FacebookAPIError as e:
                logging.error('Facebook API error: %s' % str(e))
            except IOError as e:
                logging.error(str(e))
            # uncomment to avoid waiting on already pulled pages during debugging
            # PlaceMeta.objects.get_or_create(place=place, key='debug_fb_linked')
        else:
            logging.info('skipping %s (fb id %s)' % (str(place), str(place.fb_id)))
