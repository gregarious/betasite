from django.template import Context

from django.contrib.auth.models import User
from onlyinpgh.specials.models import Coupon


class SpecialContext(Context):
    '''
    Exposes the following data:
        special (Special model instance)
        has_coupon (boolean)
    '''
    def __init__(self, special, user=None, **kwargs):
        if isinstance(user, User):
            try:
                special.coupon_set.get(user=user, was_used=False)
            except Coupon.DoesNotExist:
                has_coupon = False
            else:
                has_coupon = True
        else:
            has_coupon = False

        super(SpecialContext, self).__init__(dict(
                special=special,
                has_coupon=has_coupon),
            **kwargs)
