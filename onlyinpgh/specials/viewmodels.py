from django.contrib.auth.models import User
from onlyinpgh.specials.models import Coupon


class SpecialData(object):
    def __init__(self, special, user=None):
        if isinstance(user, User):
            try:
                special.coupon_set.get(user=user, was_used=False)
            except Coupon.DoesNotExist:
                self.has_coupon = False
            else:
                self.has_coupon = True
        else:
            self.has_coupon = False

        field_attrs = [attr for attr in special.__dict__ if not attr.startswith('_')]
        for attr in field_attrs:
            setattr(self, attr, special.__dict__[attr])
