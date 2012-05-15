'''imports all events for knowns fb-linked Places'''
from onlyinpgh.events.outsourcing import facebook
from onlyinpgh.places.models import Place
from onlyinpgh.organizations.models import Organization

import logging
logging.root.setLevel(logging.INFO)


def run():
    for place in Place.objects.exclude(fb_id=''):
        orgs = Organization.objects.filter(establishments=place)
        if orgs.count() > 0:
            logging.info(u'assigning %d owners for %s' % (orgs.count(), unicode(place)))

        try:
            facebook.add_place_events(place, orgs)
        except Exception as e:
            logging.error(e)
