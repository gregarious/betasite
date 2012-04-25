from django.contrib.auth.models import User


class SpecialData(object):
    def __init__(self, special, user=None):
        fields = ('id', 'title', 'description', 'points', 'place',
                  'dexpires', 'dstart', 'total_available', 'total_sold',
                  'tags')
        if isinstance(user, User):
            if len(special.coupon_set.filter(user=user, was_used=False)) > 0:
                self.has_coupon = True
            else:
                self.has_coupon = False
        else:
            self.has_coupon = False

        for attr in fields:
            setattr(self, attr, getattr(special, attr))
        self.pk = self.id
