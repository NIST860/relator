from django.contrib import admin
from relator.packaged import models
from relator.admin import registerer, assemblies


class PackagedUnitAdmin(admin.ModelAdmin):
	list_display = 'type', 'flow', 'vav', 'dx', 'multizone', 'tons', 'mbh'
	list_filter = 'type', 'flow', 'vav', 'dx', 'multizone'
	list_search = 'description',


class MaintenanceAdmin(admin.ModelAdmin):
	list_display = 'flow', 'type', 'min', 'max', 'cost'
	list_editable = 'cost',
	list_filter = 'flow', 'type'


class RepairAdmin(admin.ModelAdmin):
	list_display = 'tons', 'vav', 'dx', 'multizone', 'min', 'max', 'cost'
	list_editable = 'cost',

class FurnaceRepairAdmin(admin.ModelAdmin):
	list_display = 'fuel', 'mbh', 'min', 'max', 'cost'
	list_filter = 'fuel',
	list_editable = 'cost',


class ReplaceAdmin(admin.ModelAdmin):
	list_display = 'unit', 'cost'
	list_editable = 'cost',

class FurnaceReplaceAdmin(admin.ModelAdmin):
	list_display = 'fuel', 'mbh', 'min', 'max', 'cost'
	list_filter = 'fuel',
	list_editable = 'cost',


class RatesAdmin(admin.ModelAdmin):
	list_display = 'zone', 'vav', 'dx', 'multizone', 'repair', 'replace'
	list_editable = 'repair', 'replace'
	list_filter = 'vav', 'dx', 'multizone', 'zone',

class FurnaceRatesAdmin(admin.ModelAdmin):
	list_display = 'fuel', 'zone', 'repair', 'replace'
	list_editable = 'repair', 'replace'
	list_filter = 'fuel', 'zone'


register = registerer(assemblies)
register(models.SystemType, advanced=True)
register(models.PackagedUnit, PackagedUnitAdmin)
register(models.Maintenance, MaintenanceAdmin)
register(models.Repair, RepairAdmin)
register(models.Replace, ReplaceAdmin)
register(models.Rates, RatesAdmin)
register(models.FurnaceRepair, FurnaceRepairAdmin)
register(models.FurnaceReplace, FurnaceReplaceAdmin)
register(models.FurnaceRates, FurnaceRatesAdmin)
