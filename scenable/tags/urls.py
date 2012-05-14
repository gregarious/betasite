from django.conf.urls import patterns, include, url

urlpatterns = patterns('scenable.tags.views',
    url(r'^(?P<tid>\d+)/$', 'detail_page', name='tag-detail'),
)