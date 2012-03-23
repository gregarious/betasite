from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class UserProfile(models.Model):
    '''
    Extended information for any user of the site.
    '''
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )

    user = models.OneToOneField(User)
    display_name = models.TextField(max_length=30, blank=True)

    avatar_url = models.URLField(max_length=400, blank=True)
    points = models.IntegerField(default=0)

    # all of the following should be optional on a registration form
    fb_id = models.CharField(max_length=50, blank=True)
    twitter_username = models.CharField(max_length=15, blank=True)

    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    birth_year = models.IntegerField(null=True, blank=True)
    neighborhood = models.CharField(max_length=50, blank=True)

    def __unicode__(self):
        return unicode(self.user)


# signal handler to automatically create a new UserProfile
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
post_save.connect(create_user_profile, sender=User)
