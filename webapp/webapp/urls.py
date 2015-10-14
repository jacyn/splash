from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin, auth

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'webapp.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('django.contrib.auth.urls')),
    url(r'^$', 'dashboard.views.redirect_to_main'),

    url(r'^accounts/login/', 'django.contrib.auth.views.login', name='login'),
    url(r'^accounts/logout/', 'django.contrib.auth.views.logout_then_login' , name='logout'),
)

## http://stackoverflow.com/questions/19171570/a-real-example-of-url-namespace
for app in settings.LOCAL_APPS:
    urlpatterns += patterns('',
        url(r'^{0}/'.format(app), include(app + '.urls', namespace=app)),
    )

urlpatterns += patterns('', 
    url(r'^(.*)/(.*)/$', 'app.views.layout.view', name='page_view'),
)
