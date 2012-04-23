from django.conf.urls import patterns, include, url
from tastypie.api import Api
from onlyinpgh.testbed.api import PlaceResource, LocationResource, EventResource

v1_api = Api(api_name='v1')
v1_api.register(PlaceResource())
v1_api.register(LocationResource())
v1_api.register(EventResource())

urlpatterns = patterns('onlyinpgh.testbed.views',
    url(r'^$', 'home', name='testbed-home'),
    url(r'^maps$', 'maps'),
    url(r'^pipe$', 'pipe'),

    url(r'^ajax/newplace$', 'ajax_newplace'),
    url(r'^ajax/newevent$', 'ajax_newevent'),

    url(r'^api/', include(v1_api.urls)),
)
