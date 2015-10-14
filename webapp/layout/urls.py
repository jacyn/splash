from django.conf.urls import patterns, url

urlpatterns = patterns('layout.views',
    url(r'^$', 'main', name='main'),
    url(r'^objects/$', 'objects', name='objects'),
    url(r'^object/image/$', 'image', name='image'),
    url(r'^object/properties/$', 'properties', name='properties'),
    url(r'^save/$', 'save', name='save'),
    url(r'^preview/$', 'preview', name='preview'),
    )
