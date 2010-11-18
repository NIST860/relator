from django.contrib import admin
from relator.cooling import models
from relator.admin import registerer, assemblies


class ComponentAdmin(admin.ModelAdmin):
	list_display = 'number', 'tons', 'cost',
	search_fields = 'description',


class ChillerAdmin(admin.ModelAdmin):
	list_display = 'number', 'tons', 'cost', 'flow', 'type'
	list_filter = 'flow', 'type'
	search_fields = 'description',


class UpkeepAdmin(admin.ModelAdmin):
	list_display = 'min', 'max', 'cost'
	list_editable = 'cost',


class ChillerUpkeepAdmin(UpkeepAdmin):
	list_display = 'type', 'flow', 'min', 'max', 'cost'
	list_editable = 'cost',
	list_filter = 'type', 'flow'


class ReplaceAdmin(admin.ModelAdmin):
	list_display = 'unit', 'cost'
	list_editable = 'cost',


class RatesAdmin(admin.ModelAdmin):
	list_display = 'component', 'zone', 'repair', 'replace'
	list_editable = 'repair', 'replace'
	list_filter = 'component', 'zone'


class SystemAdmin(admin.ModelAdmin):
	list_display = 'price', 'tons', 'square_feet', 'chiller', 'fan_coil', 'cooling_tower'
	search_fields = 'description',

	def price(self, obj):
		from relator.utilities.templatetags.utils import price
		return price(obj.cost)


register = registerer(assemblies)
register(models.SystemType, advanced=True)

register(models.FanCoil, ComponentAdmin)
register(models.FanCoilMaintenance, UpkeepAdmin)
register(models.FanCoilRepair, UpkeepAdmin)
register(models.FanCoilReplace, ReplaceAdmin)

register(models.Chiller, ChillerAdmin)
register(models.ChillerMaintenance, ChillerUpkeepAdmin)
register(models.ChillerRepair, ChillerUpkeepAdmin)
register(models.ChillerReplace, ReplaceAdmin)

register(models.CoolingTower, ComponentAdmin)
register(models.CoolingTowerMaintenance, UpkeepAdmin)
register(models.CoolingTowerRepair, UpkeepAdmin)
register(models.CoolingTowerReplace, ReplaceAdmin)

register(models.Rates, RatesAdmin)
register(models.CoolingSystem, SystemAdmin)
