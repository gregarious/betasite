from django.http import HttpResponse
from onlyinpgh.places.models import Place

from onlyinpgh.common.utils.jsontools import jsonp_response
from onlyinpgh.common.decorators import authentication_required_403


def _make_error(status, code):
    return {
            'error': {
                'status': status,
                'code': code,
            }
        }


@authentication_required_403
@jsonp_response
def place_favorite(request):
    pid = request.GET.get('pid')
    action = request.GET.get('action')
    if pid is None:
        _make_error('invalid pid', '1')

    try:
        place = Place.objects.get(id=pid)
    except Place.DoesNotExist:
        return _make_error('invalid pid', '1')

    if action.lower() == 'favorite':
        is_action_consistent = place.mark_favorite(request.user)
    elif action.lower() == 'unfavorite':
        is_action_consistent = place.unmark_favorite(request.user)
    else:
        return _make_error('invalid action', '2')

    # if action was to favorite but favorite already existed, or vice versa, tell the client
    if is_action_consistent:
        return {'success': True}
    else:
        return _make_error('inconsistent server state', '3')


@authentication_required_403
def test(request):
    print request.user
    return HttpResponse('')
