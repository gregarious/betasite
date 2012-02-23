from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('checkin.views',
    url(r'^(?P<pid>\d+)/$', 'place_checkin'),
)
