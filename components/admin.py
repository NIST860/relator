from django.contrib import admin
from django.db.models import AutoField

class ComponentAdmin(admin.ModelAdmin):
	rates = ('maintenance_cost',
					 'repair_cost',
					 'replacement_cost')

	def __init__(self, model, admin_site):
		not_auto = lambda f: not isinstance(f, AutoField)
		other = tuple(f.name for f in filter(not_auto, model._meta.fields) if f.name not in self.rates)
		self.fields = other + self.rates
		super(ComponentAdmin, self).__init__(model, admin_site)
