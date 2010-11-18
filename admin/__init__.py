from django.contrib.admin.sites import AdminSite
from django.contrib.admin import site as admin
from django.contrib.databrowse import site as databrowse

management = AdminSite('management')
assemblies = AdminSite('assemblies')
basic = AdminSite('basic')
structure = AdminSite('structures')
types = AdminSite('types')
combined = AdminSite('combined')
advanced = AdminSite('advanced')

from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import GroupAdmin, UserAdmin
management.register(Group, GroupAdmin)
management.register(User, UserAdmin)

from django.contrib.sites.models import Site
from django.contrib.sites.admin import SiteAdmin
management.register(Site, SiteAdmin)


def registerer(*sites):
	def register(model, modeladmin=None, **kwargs):
		if kwargs.get('advanced'):
			admins = (admin, types, advanced)
		else:
			admins = sites + (admin, combined, advanced)
		for site in admins:
			site.register(model, modeladmin)
		databrowse.register(model)
	return register
