from django.contrib import admin
from relator.data import models
from relator.admin import registerer

class EnergyPlusComponentAdmin(admin.ModelAdmin):
	def name(self, obj):
		return unicode(obj)


class FuelEndUseAdmin(EnergyPlusComponentAdmin):
	list_display = 'name', 'fuel', 'heating', 'cooling', 'total'
	list_editable = 'heating', 'cooling', 'total'
	list_filter = 'fuel',


class RatioAdmin(EnergyPlusComponentAdmin):
	list_display = 'name', 'gross', 'opening'
	list_editable = 'gross', 'opening'


class WindowDataAdmin(EnergyPlusComponentAdmin):
	list_display = 'name', 'area', 'u_value', 'shgc', 'vt'
	list_editable = 'area', 'u_value', 'shgc', 'vt'


class EnergyPlusDataAdmin(admin.ModelAdmin):
	list_display = 'location', 'building', 'standard'
	list_filter = 'building', 'standard'
	search_fields = 'location',


register = registerer()
register(models.FuelEndUse, FuelEndUseAdmin)
register(models.Ratio, RatioAdmin)
register(models.WindowData, WindowDataAdmin)
register(models.EnergyPlusData, EnergyPlusDataAdmin)
