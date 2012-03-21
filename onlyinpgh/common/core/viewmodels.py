'''
Module that sets up the ViewModel system.
'''
from django.template import Context, RequestContext

from decimal import Decimal
import json


class FlattenHandler(object):
    '''
    Class to handle custom "flattening" of a particular type. Describes an
    attribute an object should be checked for, and a function that should
    be applied to the object if the attribute exists.

    e.g. For handling custom datetime flattening:
            handler = FlattenHandler('isoformat',lambda obj: obj.strftime('%Y %m %d'))
    '''
    def __init__(self, attr_name, handler=None):
        '''
        Set the handler to use the given attribute and handler function.

        If handler is not provided, the given attribute will be assumed
        to be a callable and used as the handler function.
        '''
        self.attr_name = attr_name
        if handler is None:
            self.handler = lambda obj: getattr(obj, attr_name)()
        else:
            self.handler = handler

    def __call__(self, obj):
        '''
        If obj has the given attr, return the result of running the handler
        on it. Otherwise, raise AttributeError.
        '''
        if hasattr(obj, self.attr_name):
            print 'calling', unicode(self), 'on', obj
            return self.handler(obj)
        else:
            raise AttributeError("obj has no attribute '%s'" % str(self.attr_name))

    def __unicode__(self):
        return u'"%s" handler' % unicode(self.attr_name)


class ViewModel(object):
    '''
    Abstract base class for ViewModels
    '''
    def to_data(self, custom_handlers=None):
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
        be handled correctly by _flatten()).
        '''
        # when a ViewModel is encountered, flatten it with its to_data method
        todata_handler = FlattenHandler('to_data', lambda obj: obj.to_data(custom_handlers))
        if not custom_handlers:
            custom_handlers = (todata_handler,)
        else:
            custom_handlers = custom_handlers + (todata_handler,)

        return dict([(key, _flatten(val, custom_handlers))
                        for key, val in self.__dict__.items()
                        if not key.startswith('_')])

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
        # when a date/time/datetime is encountered, don't flatten it
        date_handler = FlattenHandler('isoformat', lambda obj: obj)

        data = self.to_data(custom_handlers=(date_handler,))
        return RequestContext(request, data) if request else Context(data)


def _flatten(obj, custom_handlers=None):
    '''
    Flattens the given object to a serialization-friendly dict.

    Datatypes are handled in this order:
        - objects implementing items() (e.g. dict)
        - objects implementing  __iter__() (e.g. set, list, tuple)
            - Note: all of these objects will be turned into lists, even sets
        - numerics (int, float, long, Decimal)
        - strings
        - objects implementing isoformat() (e.g. date, time, datetime)
        - objects with __str__ or __unicode__ methods

    All others will default to unicode representations of themselves.

    Now allows the specification of a collect of custom FlattenHandler
    objects. These will be used to attempt to flatten the given object
    before the standard methods are applied. See FlattenHandler docs.
    '''

    if custom_handlers:
        for handler in custom_handlers:
            try:
                return handler(obj)
            except AttributeError:
                pass

    # handle a dict
    try:
        return dict([(k, _flatten(v, custom_handlers)) for k, v in obj.items()])
    except AttributeError:
        pass

    # handle an iterable like a tuple, set, or list as a list, but be sure
    # to not to handle a string this way
    try:
        if not isinstance(obj, basestring):
            return [_flatten(v, custom_handlers) for v in obj]
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
