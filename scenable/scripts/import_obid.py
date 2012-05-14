import csv
import os
import re
import decimal

from django.db import transaction
from django.utils.encoding import smart_unicode
from django.core.files import File
from django.template.defaultfilters import slugify

from scenable.places.models import Location, Place, PlaceMeta
from scenable.outsourcing.places import resolve_location
from scenable.common import utils

from scenable.tags.models import Tag
#from scenable.tags.categories import load_category_map
#from scenable.outsourcing.apitools import gplaces_client

from scripts import places_fb_import

import logging
logging.root.setLevel(logging.INFO)

from scenable.settings import project_file
DATA_DIR = project_file('../data')

#gplaces_category_map = load_category_map('google_places')


def run():
    # should clears all tables
    PlaceMeta.objects.all().delete()
    Place.objects.all().delete()
    Location.objects.all().delete()
    Tag.objects.all().delete()

    with open(os.path.join(DATA_DIR, 'places-all.csv')) as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            for k in row.keys():
                row[k] = smart_unicode(row[k].strip())
            rows.append(row)

    # cycle through all rows and store everything
    for idx, row in enumerate(rows):
        try:
            insert_row(row, idx)
        except Exception as e:
            logging.critical('Row %d skipped. Unexpected error: %s' % (idx, str(e)))


@transaction.commit_on_success
def insert_row(row, idx):
    logging.info(u'Importing row %d (%s)' % (int(idx), row['name']))

    try:
        lat = decimal.Decimal(row.get('lat'))
    except (TypeError, decimal.InvalidOperation):
        lat = None
    try:
        lng = decimal.Decimal(row.get('lng'))
    except (TypeError, decimal.InvalidOperation):
        lng = None
    address = row.get('street', '')

    location = Location(address=address, postcode='15213', latitude=lat, longitude=lng)
    # want to resolve location if we have an address worht normalizing and/or we don't have geocoded values
    if location.address or location.latitude is None or location.longitude is None:
        logging.info('Resolving location "%s"' % unicode(location))
        resolved = resolve_location(location)
        if resolved:
            # hack to get around Google Geocoding appending unviersity names onto many addresses
            if 'university' in resolved.address.lower() and 'university' not in row.get('street', '').lower():
                resolved.address = ','.join(resolved.address.split(',')[1:])
            resolved.address = resolved.address.strip()

            try:
                # if exact match exists, use it instead of the newly found one
                location = Location.objects.get(address=resolved.address, postcode=location.postcode)
            except Location.DoesNotExist:
                location = resolved
                location.save()
        else:
            logging.warning('Geocoding failed')

    has_corporate_fb = row.get('fb_id', '').startswith('corporate')
    place, created = Place.objects.get_or_create(
        name=row['name'],
        location=location,
        url=row.get('url', '')[:200],
        phone=row.get('phone', '')[:200],
        fb_id=row.get('fb_id', '').split(':')[-1],
        description=row.get('description', ''),
        listed=bool(int(row.get('listed', '0'))),
    )

    for t in row.get('tags', '').split(';'):
        tag, _ = Tag.objects.get_or_create(name=slugify(t.lower()))
        place.tags.add(tag)
    place.save()

    image_path = row.get('image_url', '')
    if re.match('https?\:', image_path):
        if re.match('https?\:\/\/profile.ak.fbcdn.net', image_path):
            logging.info('Skipping Facebook cdn image')
        else:
            logging.info('Pulling live image from web')
            try:
                place.image = utils.imagefile_from_url(image_path)
            except IOError:
                logging.error('Failed pulling image')
                pass
    elif image_path != '':
        logging.info('Using local image file')
        f = open(os.path.join(DATA_DIR, 'images', image_path))
        place.image = File(f)

    place.save()
    if place.image:
        place.image.close()

    if place.fb_id:
        logging.info('Supplementing info from Facebook...')
        try:
            places_fb_import.commit_place(place, corporate=has_corporate_fb)
        except places_fb_import.FacebookAPIError as e:
            logging.error('Facebook API error (fb id %s): %s' % (str(place.fb_id), unicode(e)))
        except IOError as e:
            logging.error(unicode(e))

    logging.info('Finished import: %s' % unicode(place))
    logging.info('')

    # no more Google Place lookups: have manual tags
    # # store tags from Google Place lookup
    # if location and \
    #     location.latitude is not None and location.longitude is not None:
    #     coords = (location.latitude, location.longitude)
    #     radius = 1000
    # else:
    #     coords = (40.4425, -79.9575)
    #     radius = 5000

    # response = gplaces_client.search_request(coords, radius, keyword=row.name)

    # if len(response) > 0 and 'reference' in response[0]:
    #     details = gplaces_client.details_request(response[0]['reference'])
    #     all_tags = set()
    #     for typ in details.get('types', []):
    #         if typ == 'establishment':  # skip this tag
    #             continue
    #         elif typ in gplaces_category_map:
    #             all_tags.update(gplaces_category_map[typ])
    #         else:
    #             logging.warning('Unknown Google Places type: "%s"' % typ)
    #     for tagstr in all_tags:
    #         tag, _ = Tag.objects.get_or_create(name=tagstr.lower())
    #         place.tags.add(tag)
    #     if len(all_tags) > 0:
    #         logging.debug('Row %d ("%s"): Tags [%s]' % (idx, str(row.name), ', '.join(all_tags)))
    # else:
    #     logging.warning('Row %d ("%s"): Cannot tag, no Google Places result within %dm of (%f,%f)' % \
    #         (idx, row.name, radius, coords[0], coords[1]))

    # print 'added', place