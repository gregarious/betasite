import csv, time, os, re, json

from onlyinpgh.places.models import Location, Place, Meta as PlaceMeta
from onlyinpgh.outsourcing.places import resolve_location
from onlyinpgh.identity.models import Organization
from onlyinpgh.outsourcing.models import ExternalPlaceSource, FacebookPage, FacebookOrgRecord
from onlyinpgh.tags.models import Tag
from onlyinpgh.outsourcing.fbpages import PageImportManager
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
    def __init__(self,fields):
        '''
        The following structure is assumed for the fields
        [owner,place,address,phone,url,?,fbid]
        '''
        # ensure each row is at least 6 fields long (fill with blanks if not)
        if len(fields) < 6:
            fields.extend(['']*(6-len(fields)))

        self.import_status = fields[0].lower().strip()
        self.name =    fields[1].strip()
        self.address =  fields[2].strip()
        self.phone =    fields[3].strip()
        self.url =      fields[4].strip()
        self.fb_id =    fields[5].strip()
    
    @classmethod
    def rows_from_csv(cls,csv_filename,has_header=False):
        '''
        Returns a list of OBIDRow objects from a csv file.
        '''
        with open(csv_filename) as f:
            reader = csv.reader(f)
            if HAS_HEADER:
                reader.next()
            return [OBIDRow(row) for row in reader] 
    
def run():
    #clear all tables
    Location.objects.all().delete()
    PlaceMeta.objects.all().delete()
    Place.objects.all().delete()
    Organization.objects.all().delete()
    ExternalPlaceSource.objects.all().delete()
    FacebookPage.objects.all().delete()
    FacebookOrgRecord.objects.all().delete()

    gplaces_category_map = load_category_map('google_places')

    rows = OBIDRow.rows_from_csv(CSV_FILENAME)
    
    # prefetch each fb page
    fb_rows = [row for row in rows if row.fb_id]
    page_mgr = PageImportManager()
    infos = page_mgr.pull_page_info([row.fb_id for row in fb_rows])
    for row,info in zip(fb_rows,infos):
        if isinstance(info,dict):
            row.fb_id = info['id']  # ensure a numeric id
        else:
            logger.warning('Pre-fetching fb page %s resulted in the following exception: "%s"' % (str(row.fb_id),str(info)))
            row.fb_id = ''

    # cycle through all rows and store everything
    for i,row in enumerate(rows):
        if row.import_status == 'noindex' or not row.name:
            if not row.name:
                logger.error('Row %d: No name listed. Skipping.')
            continue
        
        if row.fb_id:
            report = page_mgr.store_page(row.fb_id)  # if this fails, warnings below will kick in
            if report.model_instance:
                logger.debug('Row %d ("%s"): linked to FB page %s' % (i,row.name,report.model_instance.fb_id))
        
        organization = None
        if row.import_status == 'org' or row.import_status == 'orgonly':
            if row.fb_id:
                report = page_mgr.import_org(row.fb_id)
                if report.model_instance:
                    organization = report.model_instance
                    organization.name = row.name
                    organization.save()
                else:
                    logger.warning('Row %d ("%s"): Organization FB import notice (fbid %s, notice: "%s")' % \
                                    (i,row.name,str(row.fb_id),str(notice)))
            
            # if no fb id or the fb import failed, do it manually
            if not organization:
                organization,created = Organization.objects.get_or_create(name=row.name)
            
            if not organization.url and row.url:
                organization.url = row.url
                organization.save()
        
            logger.info('Imported %s as Organization' % row.name)

        # we're done if this is an orgonly entry
        if row.import_status == 'orgonly':
            continue

        # if we get here, the status implies the entry is a place
        
        # resolve the location
        location = resolve_location(Location(address=row.address,postcode='15213'))

        if location:
            # hack to get around Google Geocoding appending unviersity names onto many addresses
            if 'university' in location.address.lower() and 'university' not in row.address.lower():
               location.address = ','.join(location.address.split(',')[1:])

            try:
                # if exact match exists, use it instead of the newly found one
                location = Location.objects.get(address=location.address,postcode=location.postcode)
            except Location.DoesNotExist:
                location.save()
        else:
            logger.warning('Row %d ("%s"): Geocoding failed.' % (i,row.name))

        # import place
        place = None
        if row.fb_id:
            report = page_mgr.import_place(row.fb_id,import_owners=False)
            if report.model_instance:
                place = report.model_instance
                place.name = row.name
                if not place.owner and organization:     # no owner is created automatically, so set it if not created
                    place.owner = organization
                place.save()
            else:
                for notice in report.notices:
                    logger.warning('Row %d ("%s"): Place FB import notice (fbid %s, notice: "%s")' % \
                                        (i,row.name,str(row.fb_id),str(notice)))
        
        # if fb import failed, do it manually
        if not place:
            place,created = Place.objects.get_or_create(name=row.name,location=location,owner=organization)
        
        if row.url:
            PlaceMeta.objects.get_or_create(place=place,meta_key='url',defaults=dict(meta_value=row.url))
        if row.phone:
            PlaceMeta.objects.get_or_create(place=place,meta_key='phone',defaults=dict(meta_value=row.phone))

        logger.info('Imported %s as Place' % row.name)

        # store tags from Google Place lookup
        if location and \
            location.latitude is not None and location.longitude is not None:
            coords = (location.latitude,location.longitude)
            radius = 1000
        else:
            coords = (40.4425,-79.9575)
            radius = 5000

        response = gplaces_client.search_request(coords,radius,keyword=row.name)

        if len(response) > 0 and 'reference' in response[0]:
            details = gplaces_client.details_request(response[0]['reference'])
            all_tags = set()
            for typ in details.get('types',[]):
                if typ in gplaces_category_map:
                    all_tags.update(gplaces_category_map[typ])
                else:
                    logger.warning('Unknown Google Places type: "%s"' % typ)
            for tagstr in all_tags:
                tag, _ = Tag.objects.get_or_create(name=tagstr.lower())
                place.tags.add(tag)
            if len(all_tags) > 0:
                logger.debug('Row %d ("%s"): Tags [%s]' % (i,str(row.name),', '.join(all_tags)))
        else:
            logger.warning('Row %d ("%s"): Cannot tag, no Google Places result within %dm of (%f,%f)' % \
                (i,row.name,radius,coords[0],coords[1]))
