from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'onlyinpgh.orgadmin.views.page_home'),
    url(r'^home/$', 'onlyinpgh.orgadmin.views.page_home', name='orgadmin-home'),

    url(r'^signup/$', 'onlyinpgh.orgadmin.views.page_signup'),
    url(r'^login/$', 'onlyinpgh.orgadmin.views.page_login', name='orgadmin-login'),
    url(r'^logout/$', 'onlyinpgh.orgadmin.views.page_logout'),
)
