import re
import csv
import tempfile
from PIL import Image
import urllib2 as urllib
from cStringIO import StringIO

from django.core.files import File


url_pattern = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'


def process_external_url(url):
    if url:
        url_p = re.compile(url_pattern)
        if not url_p.match(url):
            url = 'http://' + url
            if not url_p.match(url):    # if that didn't work, blank out the url
                url = ''
    return url


def get_or_none(manager, **kwargs):
    '''
    Wrapper aroudn a get call that will silently return
    None if the object is not found.
    '''
    try:
        return manager.get(**kwargs)
    except manager.model.DoesNotExist:
        return None


class CSVPickler(object):
    def __init__(self, csv_fmtparam={}):
        self.fmtparam = csv_fmtparam

    def to_csv(self, tuples):
        '''
        Returns a string "pickled" in csv format. Input should be
        a collection of 1D tuple/lists.
        '''
        buff = StringIO()
        writer = csv.writer(buff, lineterminator='\n')
        for tup in tuples:
            writer.writerow(tup)
        csv_string = buff.getvalue()
        buff.close()
        return csv_string

    def from_csv(self, csv_string):
        '''
        Returns a list of tuples taken from the csv
        '''
        buff = StringIO(csv_string)
        rows = [row for row in csv.reader(buff, lineterminator='\n')]
        buff.close()
        return rows


def imagefile_from_url(url):
    '''
    Returns a django File for the image at the URL given.

    Can throw IOError on a bad URL request, or if the resulting file is an
    invalid image.
    '''
    suffix_map = {
        'jpeg': 'jpg',
        'jpg': 'jpg',
        'png': 'png',
    }
    im = Image.open(StringIO(urllib.urlopen(url).read()))
    suffix = '.' + suffix_map.get(im.format.lower(), 'jpg')
    tmp = tempfile.NamedTemporaryFile(prefix='', suffix=suffix)
    im.save(tmp)
    return File(tmp)
