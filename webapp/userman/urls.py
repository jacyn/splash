from django.conf.urls import patterns, url

urlpatterns = patterns('userman.views',
    url(r'^$', 'main', name='main'),
    url(r'^add/$', 'add', name='add'),
    url(r'^edit/(\d+)$', 'edit', name='edit'),
    url(r'^read/(\d+)/$', 'read', name='read'),
    url(r'^deactivate/(\d+)$', 'deactivate', name='deactivate'),
    url(r'^activate/(\d+)$', 'activate', name='activate'),
    url(r'^user/check/', 'check_username', name='check_username'),
    )
