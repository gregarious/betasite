from django.conf.urls import patterns, include, url

urlpatterns = patterns('onlyinpgh.tags.views',
    url(r'^(?P<tid>\d+)/$', 'detail_page', name='tag-detail'),
)