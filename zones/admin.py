from django.contrib import admin
from relator.zones import models
from relator.admin import registerer, basic

class SubzoneAdmin(admin.TabularInline):
	model = models.CensusZone

class CensusRegionAdmin(admin.ModelAdmin):
	inlines = [SubzoneAdmin]

register = registerer(basic)
register(models.Ashrae04)
register(models.Ashrae01)
register(models.HVAC)
register(models.CensusRegion, CensusRegionAdmin)
