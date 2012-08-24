from django.db import models
from sorl.thumbnail import ImageField as SorlImageField


class FeaturedImage(models.Model):
    class Meta:
        ordering = ['-dtcreated']

    dtcreated = models.DateTimeField('created datetime', auto_now_add=True)
    image = SorlImageField(upload_to='img/feat', null=True, blank=True)
    caption = models.CharField(max_length=200, null=True, blank=True)


class Notice(models.Model):
    class Meta:
        ordering = ['-dtcreated']

    dtcreated = models.DateTimeField('created datetime', auto_now_add=True)
    content = models.TextField(null=True, blank=True)
    title = models.CharField(max_length=90, null=True, blank=True)
