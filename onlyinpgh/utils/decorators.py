from django.http import HttpResponse
import json

class json_response(object):
    '''
    Decorator that transforms a function returning a bare dict into
    one that returns JSON wrapped in an HttpResponse.
    '''
    def __init__(self,fn):
        self.fn = fn
    def __call__(self, *args, **kwargs):
        data = self.fn(*args,**kwargs)
        return HttpResponse(json.dumps(data),'application/json')

class jsonp_response(object):
    '''
    Decorator that transforms a function returning a bare dict into
    one that returns JSONP wrapped in an HttpResponse.

    Decorated function must contain an argument called 'request', this
    should be an HttpRequest object. Its GET dict will be checked for a 
    'callback' element. If present, its value will be used for a JSONP
    response. If not present, a normal JSON response will be returned.
    '''
    def __init__(self,fn):
        self.fn = fn
    def __call__(self, request, *args, **kwargs):
        data = self.fn(request,*args,**kwargs)
        callback = request.GET.get('callback')

        if callback:
            response = '%s(%s);' % (callback,json.dumps(data))
            return HttpResponse(response,'application/javascript')
        else:
            response = json.dumps(data)
            return HttpResponse(response,'application/json')
