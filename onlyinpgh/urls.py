from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import redirect_to

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
#from onlyinpgh.orgadmin import urls as orgadmin_urls

admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', redirect_to, {'url': 'http://scenable.com/blog/'}),

    url(r'^prelaunch/$', 'onlyinpgh.common.views.page_home', name='home'),
    url(r'^prelaunch/login/$', 'onlyinpgh.accounts.views.page_login', name='login'),
    url(r'^prelaunch/signup/$', 'onlyinpgh.accounts.views.page_signup', name='signup'),
    url(r'^prelaunch/logout/$', 'django.contrib.auth.views.logout', name='logout', kwargs={'next_page': '/prelaunch/'}),

    url(r'^prelaunch/account/', include('onlyinpgh.accounts.urls')),

    url(r'^prelaunch/admin/', include(admin.site.urls)),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^/prelaunchadmin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^prelaunch/places/', include('onlyinpgh.places.urls')),
    url(r'^prelaunch/events/', include('onlyinpgh.events.urls')),
    url(r'^prelaunch/specials/', include('onlyinpgh.specials.urls')),
    url(r'^prelaunch/hot/$', 'onlyinpgh.hot.views.page_hot', name='hot'),

    url(r'^orgadmin/', include('onlyinpgh.orgadmin.urls')),
)
