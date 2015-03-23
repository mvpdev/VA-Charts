from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import RedirectView
from va import views, uploadsView
from va import reportsViews

urlpatterns = patterns('',
                       
    (r'^accounts/password_change/done/$', 
        'django.contrib.auth.views.password_change_done'),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^home', 'va.views.home', name='home'),
    url(r'^index/$', 'va.views.index', name='index'),
    
    #Users CRUD
    url(r'^users$', views.UsersView.as_view(), name='users_index'), #listView
    url(r'^users/create$', views.UsersCreate.as_view(), name='users_create'),
    url(r'^users/edit/(?P<pk>\d+)$', views.UpdateUsers.as_view(), name='users_edit'),
    url(r'^users/delete/(?P<pk>\d+)$', views.DeleteUsers.as_view(), name='users_delete'),
    
     #Users CRUD
    url(r'^sites$', views.SitesView.as_view(), name='sites_index'), #listView
    url(r'^sites/create$', views.SitesCreate.as_view(), name='sites_create'),
    url(r'^sites/edit/(?P<pk>\d+)$', views.UpdateSites.as_view(), name='sites_edit'),
    url(r'^sites/delete/(?P<pk>\d+)$', views.DeleteSites.as_view(), name='sites_delete'),
    
    #data upload tab
    url(r'^data/upload$', uploadsView.RawDataFilesView.as_view(), name='data_upload'), #listView
     url(r'^data/upload/new$', uploadsView.RawDataFilesCreate.as_view(), name='upload_new'),
    url(r'^data/upload/edit/(?P<pk>\d+)$', uploadsView.RawDataFilesUpdate.as_view(), name='upload_edit'),
    
     #Reports Tab
    url(r'^charts/basic-info$', 'va.reportsViews.basic_info', name='charts_basic_info'),
    url(r'^charts/issues-accessing-healthcare$', 'va.reportsViews.care_issues', name='charts_care_issues'),
    url(r'^charts/care-specifications$', 'va.reportsViews.care_specifications', name='charts_care_specifications'),
    
        
    #default
    url(r'^', RedirectView.as_view(url='/home')),
)
