from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib import databrowse
from relator.admin import (
	management,
	assemblies,
	basic,
	structure,
	types,
	combined,
	advanced,
)
from django.views.generic.simple import direct_to_template

admin.autodiscover()

urlpatterns = patterns('',
	(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
		'document_root': settings.MEDIA_ROOT}),

	(r'^admin/$', direct_to_template, {'template': 'admins.html'}),
	(r'^admin/istration/', include(admin.site.urls)),
	(r'^admin/management/', include(management.urls)),
	(r'^admin/assemblies/', include(assemblies.urls)),
	(r'^admin/basic/', include(basic.urls)),
	(r'^admin/structures/', include(structure.urls)),
	(r'^admin/combined/', include(combined.urls)),
	(r'^admin/types/', include(types.urls)),
	(r'^admin/advanced/', include(advanced.urls)),
	(r'^databrowse/(.*)', databrowse.site.root),
	(r'^', include('results.urls')),
)
