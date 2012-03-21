'''
Module that sets up the ViewModel system.
'''
from django.template import Context, RequestContext

from decimal import Decimal
import json


class ViewModel(object):
    '''
    Abstract base class for ViewModels
    '''
    def to_data(self):
        '''
        Returns a serialization-friendly dict of the member variables
        stored in this ViewModel. Base class version simply strips out
        variables with names starting with an underscore and recursively
        calls to_data on any value that is a ViewModel instance. All
        other values are assumed to be basic enough to be serializable.

        Officially, only a subset of datatypes will be extracted using
        this default implementation, all others will need to be handled
        explicitly via an overridden to_data method.

        See _flatten doctype for supported data types.

        Note that Django model classes that are also ViewModels will
        have their foreign key-based fields completely ignored as they
        are not stored in the instance's __dict__ (and moreover, cannot
        be handled correctly by _flatter()).
        '''
        return basic_data_extractor(self)

    def to_json(self):
        '''
        Returns the data as a JSON string.
        '''
        return json.dumps(self.to_data())

    def to_context(self, request=None):
        '''
        Returns a Context or RequestContext.

        RequestContext will be used if either an internally-set request
        exists, or if a request is provided via the function call.

        Calling this with a specific request object will not overwrite
        the internal request. Use set_request for this.
        '''
        return RequestContext(request, self.to_data()) if request \
                else Context(self.to_data())


def basic_data_extractor(viewmodel):
    '''
    Simple function to extract a ViewModel's member variables to a data
    dict. Will ignore underscore-led variable names.

    See _flatten doctype for supported data types.
    '''
    return dict([(key, _flatten(val))
        for key, val in viewmodel.__dict__.items()
        if not key.startswith('_')])


def _flatten(obj):
    '''
    Flattens the given object to a serialization-friendly dict. Aware of
    the ViewModel to_data method interface and will defer to this function
    whenever possible. If intact_viewmodels is True, ViewModels will be
    treated like primitives.

    Datatypes are handled in this order:
        - objects implementing to_data
        - objects implementing items() (e.g. dict)
        - objects implementing  __iter__() (e.g. set, list, tuple)
            - Note: all of these objects will be turned into lists, even sets
        - numerics (int, float, long, Decimal)
        - strings
        - objects implementing isoformat() (e.g. date, time, datetime)
        - objects with __str__ or __unicode__ methods

    All others will default to unicode representations of themselves.
    '''
    # always assume object is a ViewModel first (implements to_data)
    try:
        return obj.to_data()
    except AttributeError:
        pass

    # handle a dict
    try:
        return dict([(k, _flatten(v)) for k, v in obj.items()])
    except AttributeError:
        pass

    # handle an iterable like a tuple, set, or list as a list, but be sure
    # to not to handle a string this way
    try:
        if not isinstance(obj, basestring):
            return [_flatten(v) for v in obj]
    except TypeError:
        pass

    # handle dates/times
    try:
        return obj.isoformat()
    except AttributeError:
        pass

    # handle a decimal or float
    if isinstance(obj, float) or isinstance(obj, Decimal):
        return float(obj)

    # handle int or long
    try:
        return int(obj)
    except (TypeError, ValueError):
        pass

    # anything that makes it to here will be returned as a unicode string
    return unicode(obj)
