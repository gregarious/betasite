from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class UserProfile(models.Model):
    '''
    Extended information for any user of the site.
    '''
    user = models.OneToOneField(User)

    avatar_url = models.URLField(max_length=400, blank=True)
    points = models.IntegerField(default=0)

    fb_id = models.CharField(max_length=50, blank=True)
    twitter_username = models.CharField(max_length=15, blank=True)

    def __unicode__(self):
        return unicode(self.user)


# signal handler to automatically create a new UserProfile
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
post_save.connect(create_user_profile, sender=User)
