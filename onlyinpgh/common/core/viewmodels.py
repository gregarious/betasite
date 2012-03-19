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

        Classes derived from ViewModel that do not have member variables
        variables simple enough for this standard (e.g. Django models with
        ForeignKeys) should override to_data.
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

    Currently not built with bulletproof robustness in mind: only made to
    handle primitives, lists, dicts, and ViewModels.
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

    # handle a decimal
    if isinstance(obj, Decimal):
        return float(obj)

    # we're assuming anything that makes it to here is a primitive
    return obj
