from django.db import models
from relator.utilities.models import Type


class Fuel(Type):
	units = models.CharField(max_length=50, blank=True, default='')

class Flow(Type): pass
