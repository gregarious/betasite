from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'onlyinpgh.common.views.page_home', name='home'),

    url(r'^login/$', 'onlyinpgh.accounts.views.page_login', name='login'),
    url(r'^signup/$', 'onlyinpgh.accounts.views.page_signup', name='signup'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', name='logout', kwargs={'next_page': '/'}),

    url(r'^account/', include('onlyinpgh.accounts.urls')),

    url(r'^admin/', include(admin.site.urls)),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^manage/', include('onlyinpgh.orgadmin.urls')),

    url(r'^hot/$', 'onlyinpgh.hot.views.page_hot', name='hot'),

    url(r'^places/', include('onlyinpgh.places.urls')),
    url(r'^events/', include('onlyinpgh.events.urls')),
    url(r'^specials/', include('onlyinpgh.specials.urls')),
    url(r'^news/', include('onlyinpgh.news.urls')),
    url(r'^chatter/', include('onlyinpgh.chatter.urls')),

    url(r'^tags/', include('onlyinpgh.tags.urls')),

    # QR-code redirect handling
    url(r'^qr/$', 'onlyinpgh.common.views.qr_redirect'),
    url(r'^qr$', 'onlyinpgh.common.views.qr_redirect'),
    url(r'^qr/(\w+)/$', 'onlyinpgh.common.views.qr_redirect'),
    url(r'^qr/(\w+)$', 'onlyinpgh.common.views.qr_redirect'),

    # Scenable and Oakland shirt QRs
    url(r'^mobile-about/$', direct_to_template, {'template': 'qr/mobile_about.html'}, name='mobile-about'),
    url(r'^oakland-teaser/$', direct_to_template, {'template': 'qr/oakland_teaser.html'}, name='oakland-teaser'),

    url(r'^about/$', direct_to_template, {'template': 'qr/about.html'}, name='about'),

    # Staic pages
    # url(r^xxxxxx/$', 'onlyinpgh.common.views.page_static_xxxxxx', name='static-xxxxx'),
)

# Tastypie API setup
# # disabled for the time being
# from tastypie.api import Api
# from onlyinpgh.places.resources import PlaceFeedResource
# v1_api = Api(api_name='v1')
# v1_api.register(PlaceFeedResource())

# urlpatterns += patterns('',
#     url(r'^api/', include(v1_api.urls)),
# )


from onlyinpgh import settings
if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
    )
