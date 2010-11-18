from django.contrib import admin
from relator.insulation import models
from relator.components.admin import ComponentAdmin
from relator.admin import registerer, structure


class InsulationAdmin(ComponentAdmin):
	list_display = 'type', 'r', 'cost'
	list_editable = 'r', 'cost'
	list_filter = 'type',


register = registerer(structure)
register(models.InsulationType, advanced=True)
register(models.RigidWallInsulation, InsulationAdmin)
register(models.BlanketWallInsulation, InsulationAdmin)
register(models.RigidRoofInsulation, InsulationAdmin)
