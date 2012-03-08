from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('onlyinpgh.tags.views',
    url(r'^(?P<tid>\d+)/$', 'detail_page', name='tags-item-detail'),
)