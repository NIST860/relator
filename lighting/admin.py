from django.contrib import admin
from relator.lighting import models
from relator.components.admin import ComponentAdmin
from relator.admin import registerer, structure

register = registerer(structure)
register(models.Overhang, ComponentAdmin)
register(models.DaylightSystem, ComponentAdmin)
