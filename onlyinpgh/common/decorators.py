from django.http import HttpResponseForbidden


def authentication_required_403(view_func):
    '''
    If user not authenticated a 403 will be returned.
    '''
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated():
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()
    return wrapper
