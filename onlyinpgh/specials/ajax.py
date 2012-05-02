from onlyinpgh.specials.models import Special, Coupon

from onlyinpgh.common.utils.jsontools import jsonp_response
from onlyinpgh.common.decorators import authentication_required_403

from django.core.mail import send_mail
from smtplib import SMTPException


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


@authentication_required_403
@jsonp_response
def coupon_email(request):
    uuid = request.GET.get('uuid')

    try:
        coupon = Coupon.objects.get(uuid=uuid)
    except Coupon.DoesNotExist:
        return _make_error('invalid uuid', '1')

    if coupon.user != request.user:
        return _make_error('authorization denied', '2')
    try:
        print 'sending to', request.user.email
        # send_mail(subject=u'Scenable coupon: %s' % coupon.special.title,
        #     message=u'Access your coupon at this link: http://scenable.com%s' % coupon.get_absolute_url(),
        #     from_email=u'robot@scenable.com',
        #     recipient_list=[request.user.email])
    except SMTPException as e:
        return _make_error('problem sending: %s' % str(getattr(e, 'message', '')), '3')

    return {
        'success': True
    }
