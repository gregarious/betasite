from django.conf.urls import patterns, include, url
from tastypie.api import Api
from onlyinpgh.testbed.api import PlaceResource, LocationResource

v1_api = Api(api_name='v1')
v1_api.register(PlaceResource())
v1_api.register(LocationResource())

urlpatterns = patterns('onlyinpgh.testbed.views',
    url(r'^$', 'home', name='testbed-home'),
    url(r'^maps$', 'maps'),

    url(r'^api/', include(v1_api.urls)),
)
