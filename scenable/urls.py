from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.views.generic.simple import redirect_to, direct_to_template

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

from haystack.forms import SearchForm
from haystack.views import search_view_factory
from scenable.common.views import PageSiteSearch
from scenable import settings

from tastypie.api import Api
from scenable.places.api import PlaceResource
from scenable.places.api import CategoryResource as PlaceCategoryResource
from scenable.events.api import EventResource
from scenable.events.api import CategoryResource as EventCategoryResource
from scenable.specials.api import SpecialResource
from scenable.news.api import NewsResource
from scenable.now.api import NoticeResource, FeaturedImageResource

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', redirect_to, {'url': "http://www.scenable.com/info/"}),

    # system admin and business admin pages
    url(r'^djadmin/', include(admin.site.urls)),
    url(r'^manage/', include('scenable.orgadmin.urls')),

    # QR-code redirect handling
    url(r'^qr/$', 'scenable.common.views.qr_redirect'),
    url(r'^qr$', 'scenable.common.views.qr_redirect'),
    url(r'^qr/(\w+)/$', 'scenable.common.views.qr_redirect'),
    url(r'^qr/(\w+)$', 'scenable.common.views.qr_redirect'),

    # Scenable and Oakland shirt QRs
    url(r'^mobile-about/$', direct_to_template, {'template': 'qr/mobile_about.html'}, name='mobile-about'),
    url(r'^oakland-teaser/$', direct_to_template, {'template': 'qr/oakland_teaser.html'}, name='oakland-teaser'),

    # Static about pages for scenable.com.
    url(r'^about/$', redirect_to, {'url': '/'}, name='about'),
    url(r'^about-oakland/$', 'scenable.common.views.page_static_about_oakland', name='about-oakland'),
    url(r'^app/$', 'scenable.common.views.page_static_download_app', name='download-app'),
    url(r'^team/$', 'scenable.common.views.page_static_team', name='team'),
    url(r'^mission/$', 'scenable.common.views.page_static_mission', name='mission'),

    # Error pages
    url(r'^500\.html$', direct_to_template, {'template': '500.html'}, name='500'),
    url(r'^404\.html$', direct_to_template, {'template': '404.html'}, name='404'),
    url(r'^403\.html$', direct_to_template, {'template': '403.html'}, name='403'),

    ### TEMPORARILY REDIRECT LOGIN/SIGNUP URLS TO HOME PAGE ###
    url(r'^login/$', 'scenable.common.views.page_home', name='login'),
    url(r'^signup/$', 'scenable.common.views.page_home', name='signup'),

    url(r'^logout/$', 'django.contrib.auth.views.logout', name='logout', kwargs={'next_page': '/login/'}),

    url(r'^accounts/', include('scenable.accounts.urls')),

    #### OAKLAND CONTENT SPECIFIC URLs

    url(r'^oakland/$', 'scenable.common.views.page_oakland_home', name='beta-home'),

    url(r'^oakland/places/', include('scenable.places.urls')),
    url(r'^oakland/events/', include('scenable.events.urls')),
    url(r'^oakland/specials/', include('scenable.specials.urls')),
    url(r'^oakland/news/', include('scenable.news.urls')),
    url(r'^oakland/chatter/', include('scenable.chatter.urls')),
    url(r'^oakland/now/$', 'scenable.now.views.page_now', name='now'),

    url(r'^oakland/tags/', include('scenable.tags.urls')),

    url(r'^oakland/search/', search_view_factory(
        view_class=PageSiteSearch,
        template='search/page_site_search.html',
        form_class=SearchForm
    ), name='site-search'),
)

### TEMPORARY DISABLED MISC. UNNAMED URLS ####
#     # feedback form
#     url(r'^feedback/ajax/generic/$', 'scenable.feedback.ajax.submit_generic'),

# API setup
v1_api = Api(api_name='v1')
v1_api.register(PlaceResource())
v1_api.register(PlaceCategoryResource())
v1_api.register(EventResource())
v1_api.register(EventCategoryResource())
v1_api.register(SpecialResource())
v1_api.register(NewsResource())
v1_api.register(NoticeResource())
v1_api.register(FeaturedImageResource())

urlpatterns += patterns('',
    (r'^api/', include(v1_api.urls)),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
