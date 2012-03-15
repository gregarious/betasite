from django.db import models
from onlyinpgh.common.core.viewmodels import ViewModel


class Tag(models.Model, ViewModel):
    '''also extends ViewModel: base class's to_data handles everything'''
    name = models.SlugField()

    def __unicode__(self):
        return self.name
