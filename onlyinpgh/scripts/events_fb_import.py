'''imports all events for knowns fb-linked Places'''
from events.outsourcing import facebook
from places.models import Place

import logging
logging.root.setLevel(logging.INFO)


def run():
    for place in Place.objects.exclude(fb_id=''):
        try:
            facebook.add_place_events(place)
        except Exception as e:
            logging.error(e)
