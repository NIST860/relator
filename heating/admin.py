from django.contrib import admin
from relator.heating import models
from relator.admin import registerer, assemblies

def price(obj):
	from relator.utilities.templatetags.utils import price
	return price(obj.cost)


def fuel_names(obj):
	return ', '.join(map(str, obj.fuels.all()))
fuel_names.short_description = 'fuels'


class BoilerAdmin(admin.ModelAdmin):
	list_display = 'number', fuel_names, 'mbh', price
	list_filter = 'fuels',
	search_fields = 'description',


class EnergySupplyAdmin(admin.ModelAdmin):
	list_display = 'number', 'mbh', 'square_feet', price
	search_fields = 'description',


class RepairAdmin(admin.ModelAdmin):
	list_display = fuel_names, 'min', 'max', 'cost'
	list_editable = 'cost',


class MaintenanceAdmin(admin.ModelAdmin):
	list_display = 'type', 'min', 'max', 'cost'
	list_editable = 'cost',

	def type(self, obj):
		return obj.flow or 'Electric'


class RatesAdmin(admin.ModelAdmin):
	list_display = fuel_names, 'zone', 'repair', 'replace'
	list_editable = 'repair', 'replace'
	list_filter = 'zone',


class ReplaceAdmin(admin.ModelAdmin):
	list_display = 'unit', 'cost'
	list_editable = 'cost',


register = registerer(assemblies)
register(models.Boiler, BoilerAdmin)
register(models.BoilerFlow, advanced=True)
register(models.EnergySupply, EnergySupplyAdmin)
register(models.HeatingSystem)
register(models.BoilerRepair, RepairAdmin)
register(models.BoilerMaintenance, MaintenanceAdmin)
register(models.BoilerReplace, ReplaceAdmin)
register(models.BoilerRates, RatesAdmin)
