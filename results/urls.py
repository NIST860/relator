from django.conf.urls.defaults import *

urlpatterns = patterns('django.views.generic.simple',
		(r'^$', 'redirect_to', {'url': '/narrow/'}),
)

urlpatterns += patterns('results.views',
		(r'^narrow/$', 'narrow'),
		(r'^narrow/by-state/$', 'by_state'),
		(r'^narrow/by-region/$', 'by_region'),
		(r'^narrow/by-standard/$', 'by_standard'),
		(r'^locations/$', 'locations'),
		(r'^settings/$', 'settings'),
		(r'^results/$', 'results'),
		(r'^comparison/$', 'comparison'),
)
