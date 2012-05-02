from django.db import models
from onlyinpgh.common.core.viewmodels import ViewModel


class Tag(models.Model, ViewModel):
    '''also extends ViewModel: base class's to_data handles everything'''
    dtcreated = models.DateTimeField('created datetime', auto_now_add=True)
    name = models.SlugField(unique=True)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('tag-detail', (), {'tid': self.id})
