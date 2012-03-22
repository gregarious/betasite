import csv

from django.db import transaction

from onlyinpgh.places.models import Location, Place
from onlyinpgh.outsourcing.places import resolve_location

#from onlyinpgh.outsourcing.models import ExternalPlaceSource, FacebookPage, FacebookOrgRecord
#from onlyinpgh.outsourcing.fbpages import PageImportManager

from onlyinpgh.tags.models import Tag
from onlyinpgh.tags.categories import load_category_map
from onlyinpgh.outsourcing.apitools import gplaces_client
# from onlyinpgh.outsourcing.apitools.facebook import oip_client as fb_client

import logging
logging.disable(logging.INFO)
logger = logging.getLogger('onlyinpgh.obidimport')

from onlyinpgh.settings import to_abspath
CSV_FILENAME = to_abspath('../data/obid.csv')
HAS_HEADER = True


class OBIDRow:
    def __init__(self, fields):
        '''
        The following structure is assumed for the fields
        [owner,place,address,phone,url,?,fbid]
        '''
        # ensure each row is at least 6 fields long (fill with blanks if not)
        if len(fields) < 6:
            fields.extend([''] * (6 - len(fields)))

        self.import_type = fields[0].lower().strip()
        self.name = fields[1].strip()
        self.address = fields[2].strip()
        self.phone = fields[3].strip()
        self.url = fields[4].strip()
        self.fb_id = fields[5].strip()

    @classmethod
    def rows_from_csv(cls, csv_filename, has_header=False):
        '''
        Returns a list of OBIDRow objects from a csv file.
        '''
        with open(csv_filename) as f:
            reader = csv.reader(f)
            if HAS_HEADER:
                reader.next()
            return [OBIDRow(row) for row in reader]

gplaces_category_map = load_category_map('google_places')


def run():
    # should clears all tables
    Place.objects.all().delete()
    Location.objects.all().delete()
    Tag.objects.all().delete()

    rows = OBIDRow.rows_from_csv(CSV_FILENAME)

    # prefetch each fb page
    # TODO: reenable facebook pulling
    # page_mgr = PageImportManager()
    # fb_rows = [row for row in rows if row.fb_id]
    # infos = page_mgr.pull_page_info([row.fb_id for row in fb_rows])
    # for row, info in zip(fb_rows, infos):
    #     if isinstance(info, dict):
    #         row.fb_id = info['id']  # ensure a numeric id
    #     else:
    #         logger.warning('Pre-fetching fb page %s resulted in the following exception: "%s"' % (str(row.fb_id), str(info)))
    #         row.fb_id = ''

    # cycle through all rows and store everything
    for idx, row in enumerate(rows):
        insert_row(row, idx)


@transaction.commit_on_success
def insert_row(row, idx=None):
    if row.import_type == 'noindex':
        return
    if not row.name:
        logger.error('Row %d: No name listed. Skipping.')
        return

    # # TODO: reenable facebook pulling
    # if row.fb_id:
    #     report = page_mgr.store_page(row.fb_id)  # if this fails, warnings below will kick in
    #     if report.model_instance:
    #         logger.debug('Row %d ("%s"): linked to FB page %s' % (idx, row.name, report.model_instance.fb_id))

    # resolve the location
    location = resolve_location(Location(address=row.address.strip(), postcode='15213'))

    if location:
        # hack to get around Google Geocoding appending unviersity names onto many addresses
        if 'university' in location.address.lower() and 'university' not in row.address.lower():
            location.address = ','.join(location.address.split(',')[1:])
        location.address = location.address.strip()

        try:
            # if exact match exists, use it instead of the newly found one
            location = Location.objects.get(address=location.address, postcode=location.postcode)
        except Location.DoesNotExist:
            location.save()
    else:
        logger.warning('Row %d ("%s"): Geocoding failed.' % (idx, row.name))

    # import place
    place = None
    # TODO: reenable facebook integration
    # if row.fb_id:
    #     report = page_mgr.import_place(row.fb_id, import_owners=False)
    #     if report.model_instance:
    #         place = report.model_instance
    #         place.name = row.name
    #         place.save()
    #     else:
    #         for notice in report.notices:
    #             logger.warning('Row %d ("%s"): Place FB import notice (fbid %s, notice: "%s")' % \
    #                             (idx, row.name, str(row.fb_id), str(notice)))

    # if fb import failed, do it manually
    if not place:
        place, created = Place.objects.get_or_create(
            name=row.name,
            location=location,
            url=row.url[:200],
            phone=row.phone[:200],
            fb_id=row.fb_id,
            )

    logger.info('Imported %s as Place' % row.name)

    # store tags from Google Place lookup
    if location and \
        location.latitude is not None and location.longitude is not None:
        coords = (location.latitude, location.longitude)
        radius = 1000
    else:
        coords = (40.4425, -79.9575)
        radius = 5000

    response = gplaces_client.search_request(coords, radius, keyword=row.name)

    if len(response) > 0 and 'reference' in response[0]:
        details = gplaces_client.details_request(response[0]['reference'])
        all_tags = set()
        for typ in details.get('types', []):
            if typ == 'establishment':  # skip this tag
                continue
            elif typ in gplaces_category_map:
                all_tags.update(gplaces_category_map[typ])
            else:
                logger.warning('Unknown Google Places type: "%s"' % typ)
        for tagstr in all_tags:
            tag, _ = Tag.objects.get_or_create(name=tagstr.lower())
            place.tags.add(tag)
        if len(all_tags) > 0:
            logger.debug('Row %d ("%s"): Tags [%s]' % (idx, str(row.name), ', '.join(all_tags)))
    else:
        logger.warning('Row %d ("%s"): Cannot tag, no Google Places result within %dm of (%f,%f)' % \
            (idx, row.name, radius, coords[0], coords[1]))

    print 'added', place
