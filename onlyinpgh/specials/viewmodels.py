from django.contrib.auth.models import User
from onlyinpgh.specials.models import Coupon


class SpecialData(object):
    def __init__(self, special, user=None):
        fields = ('id', 'title', 'description', 'points', 'place',
                  'dexpires', 'dstart', 'total_available', 'total_sold',
                  'tags')
        if isinstance(user, User):
            try:
                special.coupon_set.get(user=user, was_used=False)
            except Coupon.DoesNotExist:
                self.has_coupon = False
            else:
                self.has_coupon = True
        else:
            self.has_coupon = False

        for attr in fields:
            setattr(self, attr, getattr(special, attr))
