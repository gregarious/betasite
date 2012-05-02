from onlyinpgh.specials.models import Special

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
def coupon_buy(request):
    sid = request.GET.get('sid')
    if sid is None:
        _make_error('invalid sid', '1')

    try:
        special = Special.objects.get(id=sid)
    except Special.DoesNotExist:
        return _make_error('invalid sid', '1')

    coupon = special.assign_coupon(request.user)
    return {
        'success':
            {'uuid': str(coupon.uuid)}
        }
