from django.contrib import admin
from relator.standards import models
from forms import current_element_form
from relator.admin import registerer, basic

class RoofValueAdmin(admin.ModelAdmin):
	list_display = 'roof', 'standard', 'zone', 'r'
	list_editable = 'r',
	list_filter = 'roof', 'standard',
	form = current_element_form(models.RoofValue, 'roof')


class WallValueAdmin(admin.ModelAdmin):
	list_display = 'wall', 'standard', 'zone', 'r'
	list_editable = 'r',
	list_filter = 'wall', 'standard',
	form = current_element_form(models.WallValue, 'wall')


class OverhangDataAdmin(admin.ModelAdmin):
	list_display = 'standard', 'overhang', 'czones'
	list_filter = 'standard', 'overhang'

	def czones(self, obj):
		return ','.join(map(str, obj.zones.all()))
	czones.short_description = 'zones'


class StandardAdmin(admin.ModelAdmin):
	list_display = 'name', 'zone_type'


register = registerer(basic)
register(models.Standard, StandardAdmin)
register(models.RoofValue, RoofValueAdmin)
register(models.WallValue, WallValueAdmin)
register(models.OverhangData, OverhangDataAdmin)
