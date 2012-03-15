from django.db import models


class Tag(models.Model):
    '''also extends ViewModel: base class's to_data handles everything'''
    name = models.SlugField()

    def __unicode__(self):
        return self.name
