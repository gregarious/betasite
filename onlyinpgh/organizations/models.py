from django.db import models
from django.contrib.auth.models import User
from onlyinpgh.places.models import Place


class Organization(models.Model):
    '''
    Represents organizations in the community (business, charity, etc.)
    '''
    name = models.CharField(u'Organization name', max_length=200)
    dtcreated = models.DateTimeField(u'Datetime created', auto_now_add=True)

    administrators = models.ManyToManyField(User, verbose_name=u'Users with administrator access',
        blank=True, null=True)
    establishments = models.ManyToManyField(Place, verbose_name=u'Establishments owned',
        blank=True, null=True)

    image = models.ImageField(upload_to='img/o', null=True, blank=True)
    url = models.URLField('Website', blank=True)
    fb_id = models.CharField('Facebook ID', max_length=50, blank=True)
    twitter_username = models.CharField(u'Twitter username', max_length=15, blank=True)

    def __unicode__(self):
        return self.name
