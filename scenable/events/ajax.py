import time

from scenable.events.models import Event

from scenable.common.utils.jsontools import jsonp_response
from scenable.common.decorators import authentication_required_403


def _make_error(status, code):
    return {
            'error': {
                'status': status,
                'code': code,
            }
        }


@authentication_required_403
@jsonp_response
def event_attend(request):
    eid = request.GET.get('eid')
    action = request.GET.get('action')
    if eid is None:
        _make_error('invalid eid', '1')

    try:
        event = Event.objects.get(id=eid)
    except Event.DoesNotExist:
        return _make_error('invalid eid', '1')

    if action.lower() == 'attend':
        is_action_consistent = event.add_attendee(request.user)
    elif action.lower() == 'unattend':
        is_action_consistent = event.remove_attendee(request.user)
    else:
        return _make_error('invalid action', '2')

    # if action was to attend but attendance already existed, or vice versa, tell the client
    if is_action_consistent:
        return {'success': True}
    else:
        return _make_error('inconsistent server state', '3')
