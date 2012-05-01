from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from onlyinpgh.common.core.viewmodels import ViewModel


class UserProfile(models.Model, ViewModel):
    '''
    Extended information for any user of the site.
    '''
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )

    user = models.OneToOneField(User)
    display_name = models.CharField(max_length=30, blank=True)

    avatar = models.ImageField(upload_to='img/a', null=True, blank=True)
    points = models.IntegerField(default=0)

    # all of the following should be optional on a registration form
    fb_id = models.CharField(max_length=50, blank=True)
    fb_id_public = models.BooleanField(default=True)

    twitter_username = models.CharField(max_length=15, blank=True)
    twitter_username_public = models.BooleanField(default=True)

    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    neighborhood = models.CharField(max_length=50, blank=True)

    def __unicode__(self):
        return unicode(self.user)

    def to_data(self, *args, **kwargs):
        '''
        Manually choose and insert user information. Note that
        two ids are produced in the data output: id (User.id)
        and profile_id (UserProfile.id).
        '''
        data = super(UserProfile, self).to_data(*args, **kwargs)
        data['profile_id'] = self.id
        data.pop('user_id')
        user_fields = ('id', 'username', 'email')
        for k in user_fields:
            data[k] = getattr(self.user, k)
        return data

    def display_or_username(self):
        return self.display_name if self.display_name else self.user.username


# signal handler to automatically create a new UserProfile
def create_user_profile(sender, instance, created, **kwargs):
    # raw will be true when loaddata script is run (will run
    # into a db uniqueness conflict if we have a fixture that
    # tried to load corresponding profiles)
    if created and not kwargs.get('raw', False):
        UserProfile.objects.create(user=instance)
post_save.connect(create_user_profile, sender=User)
