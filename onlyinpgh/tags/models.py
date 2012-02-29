from django.db import models

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from onlyinpgh.common.core.viewmodels import ViewModel, RenderableViewModel

class Tag(models.Model,ViewModel):
	'''also extends ViewModel: base class's to_data handles everything'''
	name = models.SlugField()

	def __unicode__(self):
		return self.name

# class TaggedItem(models.Model):
#     tag = models.ForeignKey(Tag)
#     content_type = models.ForeignKey(ContentType)
#     object_id = models.PositiveIntegerField()
#     content_object = generic.GenericForeignKey('content_type', 'object_id')

#     def __unicode__(self):
#         return u'%s => (%s)' % (unicode(self.tag),unicode(self.content_object))