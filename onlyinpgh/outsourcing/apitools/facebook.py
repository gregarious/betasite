import urllib
import urllib2
import json
import time
import re


class FacebookAPIError(IOError):
    '''
    Facebook API specific IOError. Can be constructed directly from an
    error response dict resulting from a failed API call.

    Known codes:
    - 21: page migrated
    '''
    def __init__(self, message='', error_dict={}):
        self.code = str(error_dict.get('code', ''))
        self.type = error_dict.get('type', 'Unknown')
        super(FacebookAPIError, self).__init__(error_dict.get('message', message))

    def is_migration_error(self):
        return self.code == '21'

    def get_migration_destination(self):
        '''
        If the given error is a migration error, return the new ID that
        the page has moved to.
        '''
        if not self.is_migration_error():
            return None
        match = re.search('ID (\d+) was migrated to page ID (\d+)', self.message)
        if match:
            return match.group(2)
        else:
            # TODO: need to notify admin that the migration error message may have changed
            return None


def get_basic_access_token(client_id, client_secret):
    '''
    Quick utility function to generate a basic access token given an app id
    and secret values. Shouldn't need
    '''
    query = {'client_id':      client_id,
             'client_secret':  client_secret,
             'grant_type':     'client_credentials'}

    url = 'https://graph.facebook.com/oauth/access_token?' + urllib.urlencode(query)
    response = urllib2.urlopen(url).read()

    try:
        key, val = response.split('=')
        if key == 'access_token':
            return val
    except ValueError:  # be silent for now, it will be reported below
        pass

    raise FacebookAPIError('Access token retreival error.')


class GraphAPIClient(object):
    def __init__(self, access_token=None):
        self.access_token = access_token

    def _make_request(self, request, timeout=None, retry_limit=1):
        '''
        Helper function to make Graph API requests and handle timeout and
        possible error conditions.

        Will throw an IOError with a low-level problem (e.g. timeout,
        connection refused, FacebookAPIError on a bad response from the
        API service.

        Any falsey timeout value will be treated as no timeout.
        '''
        try:
            if timeout:
                response = json.load(urllib2.urlopen(request, timeout=timeout))
            else:
                response = json.load(urllib2.urlopen(request))
        except urllib2.HTTPError as http_err:
            # urllib2 will throw an HTTPError if the HTTP request was unsuccessful. this error
            # can contain useful info if the actual content of the response had error content,
            # so we look into this content for error information
            try:
                response = json.load(http_err.fp)
            except Exception:       # don't mess around here. if error's file can't be read for any reason, we punt
                response = None
            if response is None or 'error' not in response:    # raise it out here to get full stack trace
                raise

        # result post-processing
        if response == []:
            raise FacebookAPIError(u"empty list response returned")
        elif response == False:
            raise FacebookAPIError(u"'false' response returned")
        elif response is None:
            raise FacebookAPIError(u"null response returned")
        elif 'error' in response:
            raise FacebookAPIError(error_dict=response['error'])
        # TODO: remember to handle error code 21!
        return response

        # TODO: commented out old method of throttle handling. uncomment after
        # learning more about FB throttling errors.
        # assert(self.throttle_wait >= 0)  # if this isn't true, retry logic could allow exceeding timeout
        # tend = (time.time() + timeout) if timeout is not None else float('inf')
        # retry_count = 0
        # while True:
        #     try:
        #         if tend != float('inf'):
        #             tleft = tend - time.time()
        #             if tleft <= 0:
        #                 raise urllib2.URLError(socket.timeout('timed out'))
        #             print '  Request:', request
        #             print '  Allowed time:', tleft
        #             response = json.load(urllib2.urlopen(request, timeout=tleft))
        #         else:
        #             response = json.load(urllib2.urlopen(request))
        #     except IOError:
        #         # check that the throttle wait doesn't exceed our retry limit
        #         if self.throttle_wait > tend - time.time():
        #             raise
        #         # if we're out of retries -- just raise the error
        #         if retry_count >= retry_limit:
        #             raise
        #         retry_count += 1
        #         time.sleep(self.throttle_wait)
        #     else:
        #         return self.postprocess_response(response)

    def graph_api_page_request(self, fb_id, metadata=False, timeout=None, retry_limit=1):
        '''
        Convenience method to query the Graph API for a page object.

        Will always return metadata. To customize this, use
        graph_api_object_request.

        Will fail with a TypeError if the returned object isn't a page.
        '''
        page_info = self.graph_api_object_request(fb_id, metadata=True, timeout=timeout, retry_limit=1)
        if page_info.get('type') != 'page':
            raise TypeError("Expected 'page' object from Graph API. Received '%s'." % page_info.get('type'))
        if not metadata:
            page_info.pop('metadata')
        return page_info

    def graph_api_picture_request(self, fb_id, size='normal', timeout=None):
        '''
        Returns the url to the picture connected to the given object.

        size can be among 'small', 'normal', 'large'.
        '''
        url = 'http://graph.facebook.com/%s/picture?type=%s' % (fb_id, size)
        if timeout is None:
            response = urllib2.urlopen(url)
        else:
            response = urllib2.urlopen(url, timeout=timeout)
        return response.url

    def graph_api_object_request(self, fb_id, metadata=False, timeout=None, retry_limit=1):
        '''
        Returns a dict of data for given Graph API object.

        If metadata is True, the metadata argument will be enabled on the
        call, returning supplemental introspective fields for the object
        under the 'metadata' key (a root-level "type" key will also be
        part of the results).

        Will raise IOError if response could not be received from the API
        service. Any problem with response content will raise a
        FacebookAPIError.
        '''
        get_opts = {}
        if self.access_token:
            get_opts['access_token'] = self.access_token
        if metadata:
            get_opts['metadata'] = 1

        query_string = urllib.urlencode(get_opts)
        request_url = 'https://graph.facebook.com/' + fb_id
        if len(get_opts) > 0:
            request_url += '?' + query_string

        # handles retries and exception handling
        return self._make_request(request_url, timeout=timeout, retry_limit=retry_limit)

    def graph_api_multiobject_request(self, fb_ids, metadata=False, timeout=None, retry_limit=1):
        '''
        Does a "psuedo-batch" request for multiple objects with known
        Facebook ids. Input is a list of ids (numbers or strings OK),
        output is a parallel list of response dicts.

        Be careful with this, if any of the requests are bad, the whole
        thing will fail.

        See graph_api_object_request for metadata details.

        Will raise IOError if response could not be received from the API
        service. Any problem with response content will raise a
        FacebookAPIError.
        '''
        get_opts = {'ids': ', '.join(map(str, fb_ids))}
        if self.access_token:
            get_opts['access_token'] = self.access_token
        if metadata:
            get_opts['metadata'] = 1

        query_string = urllib.urlencode(get_opts)
        request_url = 'https://graph.facebook.com/?' + query_string

        # handles retries and exception handling
        response = self._make_request(request_url, timeout=timeout, retry_limit=retry_limit)

        # result will be a dict indexed by facebook id
        return [response[fb_id] for fb_id in fb_ids]

    def graph_api_collection_request(self, suburl, max_pages=10, timeout=None, retry_limit=1, **kw_options):
        '''
        Thin wrapper around Graph API query that returns pages of 'data' arrays.
        kw_options can take any option that the graph query could take.

        e.g. - graph_api_collection_request('cocacola/events')
                for all events connected to Coca-Cola
             - graph_api_collection_request('search', q=coffee,
                                        type=place,
                                        center=37.76, -122.427,
                                        distance=1000)
                for all pages with coffee in the name 1km from (37.76, -122.427)
            See https://developers.facebook.com/docs/reference/api/ for more.

        Paging will be automatically followed up to max_pages requests. This
        limit can be disabled by setting it to None or a non-positive number.
        A runaway query could run for a VERY long time, hence the need to
        explicitly disabling the max pages.

        timeout is the allowed time for ALL paging requests to finish (this is
        always AT LEAST 2 requests, since we don't know we're done till we hit
        an empty request), so this multiplicative effect should be considered if
        using a timeout.
        '''
        if max_pages < 1:
            max_pages = None

        get_args = {}
        if self.access_token:
            get_args = {'access_token': self.access_token}
        if kw_options:
            get_args.update(kw_options)

        request_url = 'https://graph.facebook.com/' + suburl
        if get_args:
            request_url += '?' + urllib.urlencode(get_args)

        all_data = []
        pages_read = 0
        # inside loop because results might be paged
        tstart = time.time()
        while request_url:
            tleft = timeout - (time.time() - tstart) if timeout is not None else None
            # handles retries and exception handling
            response = self._make_request(request_url, timeout=tleft, retry_limit=retry_limit)

            if 'data' not in response:
                raise FacebookAPIError("Expected response: no 'data' field")

            all_data.extend(response['data'])

            # if there's more pages to the results, fb gives a handy url to go to next page
            if 'paging' in response and 'next' in response['paging']:
                request_url = response['paging']['next']
                pages_read += 1
            else:
                request_url = ''

            if max_pages is not None and pages_read >= max_pages:
                break

        return all_data
