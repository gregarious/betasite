from django.db import models
from django.contrib.auth.models import User


class BasicSurveyResponse(models.Model):
    general_feedback = models.TextField(verbose_name=u'What would make this page better?', blank=True)

    user = models.ForeignKey(User)
    page = models.CharField(max_length=50, blank=True)

    def save(self, *args, **kwargs):
        if self.Meta.page:
            self.page = self.Meta.page
        super(BasicSurveyResponse, self).save(*args, **kwargs)


class PlaceFeedSurveyResponse(BasicSurveyResponse):
    class Meta:
        page = 'place_feed'

    MODES = (
        ('map', 'Map'),
        ('feed', 'Feed')
    )
    mode_used_first = models.CharField(verbose_name=u'What did you use first upon coming to this page?',
                                        blank=True, choices=MODES)


class PlaceDetailSurveyResponse(BasicSurveyResponse):
    class Meta:
        page = 'place_detail'


class EventFeedSurveyResponse(BasicSurveyResponse):
    class Meta:
        page = 'event_feed'

###


class xSurveyResponse(BasicSurveyResponse):
    class Meta:
        page = ''
