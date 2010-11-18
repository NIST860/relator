from django.contrib.admin import site as all
from relator.admin import registerer, assemblies
from relator.assemblies import models

register = registerer(assemblies)
register(models.Fuel, advanced=True)
register(models.Flow, advanced=True)
