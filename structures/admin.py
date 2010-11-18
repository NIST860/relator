from django.contrib import admin
from relator.structures import models
from relator.admin import registerer, basic, structure

class BuildingAdmin(admin.ModelAdmin):
	list_display = 'type', 'life'
	list_filter = 'wall', 'roof'


class CostAdmin(admin.ModelAdmin):
	list_filter = 'building', 'year'


register = registerer(basic, structure)
register(models.Roof)
register(models.Wall)
register(models.Building, BuildingAdmin)
register(models.Cost, CostAdmin)
