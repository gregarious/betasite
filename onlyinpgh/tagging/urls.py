from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('tagging.views',
    url(r'^(?P<tid>\d+)/$', 'detail_page', name='tagging-item-detail'),
)