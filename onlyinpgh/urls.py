from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import redirect_to, direct_to_template

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

    url(r'^manage/', include('onlyinpgh.orgadmin.urls')),

    # QR-code redirect handling
    url(r'^qr/$', 'onlyinpgh.common.views.qr_redirect'),
    url(r'^qr$', 'onlyinpgh.common.views.qr_redirect'),
    url(r'^qr/(\w+)/$', 'onlyinpgh.common.views.qr_redirect'),
    url(r'^qr/(\w+)$', 'onlyinpgh.common.views.qr_redirect'),

    # Scenable and Oakland shirt QRs
    url('mobile-about', direct_to_template, {'template': 'qr/mobile_about.html'}, name='mobile-about'),
    url('oakland-teaser', direct_to_template, {'template': 'qr/oakland_teaser.html'}, name='oakland-teaser'),

    # Static about page for the scenable.com - not in use
    url('about', direct_to_template, {'template': 'qr/about.html'}, name='about'),
)
