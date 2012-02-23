from django.db import models
from django.contrib.auth.models import User

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

class Identity(models.Model):
    class Meta:
        verbose_name_plural = 'identities'
        ordering = ['name']

    dt_created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100)
    
    # account is not required to have an identity on the site
    account = models.ManyToManyField(User,null=True,blank=True)
    avatar = models.URLField(blank=True)

    def __unicode__(self):
        return self.name

class Organization(Identity):
    url = models.URLField(max_length=400,blank=True)

class Individual(Identity):
    pass

class FavoriteItem(models.Model):
    user = models.ForeignKey(User)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return u'%s => %s' % (unicode(self.account),unicode(self.content_object))