from django.contrib import admin
from relator.locations import models
from relator.admin import registerer, basic

def state_code(obj):
	return obj.state.code
state_code.short_description = 'State'


class LocationIndexInlineAdmin(admin.TabularInline):
	model = models.LocationIndexValue


class LocationAdmin(admin.ModelAdmin):
	list_display = 'name', state_code, 'county', 'representative'
	list_editable = 'representative',
	list_filter = 'state',
	search_fields = 'name',
	inlines = [LocationIndexInlineAdmin]


class CountyAdmin(admin.ModelAdmin):
	list_display = 'name', state_code, 'cities'
	list_filter = 'state',
	search_fields = 'name',

	def cities(self, obj):
		return ', '.join(loc.name for loc in obj.locations.all())


class StateAdmin(admin.ModelAdmin):
	list_display = 'name', 'code', 'census_zone'
	list_filter = 'census_zone',
	search_fields = 'name', 'code'


class LocationIndexValueAdmin(admin.ModelAdmin):
	list_display = 'location', 'index', 'value'
	list_editable = 'value',
	list_filter = 'index',
	search_fields = 'location__name',


class IndexAdmin(admin.ModelAdmin):
	list_display = 'name', 'description'
	inlines = [LocationIndexInlineAdmin]

register = registerer(basic)
register(models.State, StateAdmin)
register(models.County, CountyAdmin)
register(models.Location, LocationAdmin)
register(models.Index, IndexAdmin, advanced=True)
register(models.LocationIndexValue, LocationIndexValueAdmin)
