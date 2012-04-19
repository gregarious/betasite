from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import redirect_to, direct_to_template

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
#from onlyinpgh.orgadmin import urls as orgadmin_urls

admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', redirect_to, {'url': 'http://scenable.com/about/'}),

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
    url(r'^mobile-about/$', direct_to_template, {'template': 'qr/mobile_about.html'}, name='mobile-about'),
    url(r'^oakland-teaser/$', direct_to_template, {'template': 'qr/oakland_teaser.html'}, name='oakland-teaser'),

    # Static about page for the scenable.com - not in use
    url(r'^about/$', direct_to_template, {'template': 'qr/about.html'}, name='about'),

    url('chatter_example', 'onlyinpgh.common.views.example_chatter', name='example_chatter'),
    url('news_example', 'onlyinpgh.common.views.example_news', name='example_news'),

    #url(r'^tags/',include('onlyinpgh.tags.urls')),

    # url(r'^$', home_views.hot_page),
    # url(r'^map$', home_views.map_page),
    # url(r'^grabbit$', home_views.checkin_page),
    # url(r'^specials$', offers_views.offers_page),
    # url(r'^news$', news_views.news_page),
    # url(r'^events$', events_views.events_page),
    # url(r'^places$', places_views.places_page),
    # url(r'^search$', home_views.search_page),
    # url(r'^tags$', tag_views.all_tags),

    # url(r'^chatter$', chatter_views.chatter_posts_hot),
    # url(r'^chatter/new$', chatter_views.chatter_posts_new),
    # url(r'^chatter/questions$', chatter_views.chatter_posts_questions),
    # url(r'^chatter/discuss$', chatter_views.chatter_posts_conversations),
    # url(r'^chatter/pics$', chatter_views.chatter_posts_photos),

    # url(r'^chatter/(?P<id>\d+)/$', chatter_views.single_post_page),
    # url(r'^chatter/post-form/$', chatter_views.post_form),

    # url(r'^specials/(?P<id>\d+)/$', offers_views.single_offer_page),
    # url(r'^news/(?P<id>\d+)/$', news_views.single_article_page),
    # url(r'^events/(?P<id>\d+)/$', events_views.single_event_page),
    # url(r'^places/(?P<id>\d+)/$', places_views.single_place_page),

    # # OBID app urls
    # url(r'^ajax/places_feed$', places_views.ajax_places_feed),
    # url(r'^ajax/events_feed$', events_views.ajax_events_feed),
    # url(r'^ajax/event/(?P<eid>\d+)/$', events_views.ajax_event_item),

    # url(r'^ajax/hot_feed$', home_views.ajax_hot_page)
    # #url(r'^ajax/specials_feed$', offers_views.ajax_specials_feed),
)
