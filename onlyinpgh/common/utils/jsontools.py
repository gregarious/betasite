from django.http import HttpResponse
from django.utils.safestring import mark_safe
import json


def package_json_response(data, request=None):
    '''
    Packages the data dict into an JSON HttpResponse object. Will return a
    JSONP response if request is given and request has a GET argument
    named 'callback'.
    '''
    if request and request.GET.get('callback'):
        response = '%s(%s);' % (request.GET.get('callback'),
                                json.dumps(data))
        return HttpResponse(response, 'application/javascript')

    response = json.dumps(data)
    return HttpResponse(response, 'application/json')


class json_response(object):
    '''
    Decorator that transforms a function returning a bare dict into
    one that returns JSON wrapped in an HttpResponse.
    '''
    def __init__(self, fn):
        self.fn = fn

    def __call__(self, *args, **kwargs):
        data = self.fn(*args, **kwargs)
        return package_json_response(data)


class jsonp_response(object):
    '''
    Decorator that transforms a function returning a bare dict into
    one that returns JSONP wrapped in an HttpResponse.

    Decorated function must contain an argument called 'request', this
    should be an HttpRequest object. Its GET dict will be checked for a
    'callback' element. If present, its value will be used for a JSONP
    response. If not present, a normal JSON response will be returned.
    '''
    def __init__(self, fn):
        self.fn = fn

    def __call__(self, request, *args, **kwargs):
        data = self.fn(request, *args, **kwargs)
        return package_json_response(data, request)


def sanitize_json(json_string):
    '''
    Removes any occurances of </ from a string and marks it as safe.
    '''
    return mark_safe(json_string.replace('</', '\<\/'))


def serialize_resource(resource, obj=None, data=None, request=None, sanitize=True):
    '''
    Use the given Tastypie Resource instance to pack up the object/data
    into a JSON-serialized resource.
    '''
    bundle = resource.build_bundle(request=request, obj=obj, data=data)
    dehydrated = resource.full_dehydrate(bundle)
    json = resource.serialize(None, dehydrated, 'application/json')
    if sanitize:
        return sanitize_json(json)
    else:
        return json


def serialize_resources(resource, objs, request=None, sanitize=True):
    '''
    Use the given Tastypie Resource instance to pack up the objects
    into a JSON-serialized array of resources.
    '''
    bundles = (resource.build_bundle(request=request, obj=obj) for obj in objs)
    dehydrated = [resource.full_dehydrate(bundle) for bundle in bundles]
    json = resource.serialize(None, dehydrated, 'application/json')
    if sanitize:
        return sanitize_json(json)
    else:
        return json
