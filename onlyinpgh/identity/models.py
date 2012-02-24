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

class FavoriteManager(models.Manager):
    def _by_type_call(self,call,model_type=None,model_instance=None,**kwargs):
        '''helper for *_by_type calls'''
        if model_type:
            kwargs['content_type'] = ContentType.objects.get_for_model(model_type)
        if model_instance:
            kwargs['object_id'] = model_instance.id
            # need a content_type argument to ensure object_id refers to the correct model type
            if 'content_type' not in kwargs:
                kwargs['content_type'] = ContentType.objects.get_for_model(model_instance.__class__)
        return call(**kwargs)

    def get_by_type(self,model_type=None,model_instance=None,**kwargs):
        '''
        Wrapper around normal get call that only finds FavoriteItems that 
        tied to a specific model type or instance.
        '''
        return self._by_type_call(FavoriteItem.objects.get,
                                    model_type,model_instance,**kwargs)

    def filter_by_type(self,model_type=None,model_instance=None,**kwargs):
        '''
        Wrapper around normal filter call that only finds FavoriteItems that 
        tied to a specific model type or instance.
        '''
        return self._by_type_call(FavoriteItem.objects.filter,
                                    model_type,model_instance,**kwargs)

class FavoriteItem(models.Model):
    user = models.ForeignKey(User)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    objects = FavoriteManager()

    def __unicode__(self):
        return u'%s => %s' % (unicode(self.user),unicode(self.content_object))