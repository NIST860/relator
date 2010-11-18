from django.db import models
from relator.units import fields
from relator.units.fields import uscs
from relator.constants.models import ConstantMRRModel

class Component(ConstantMRRModel):
	cost = uscs.CostPerSquareFootField()
	maintenance_cost = fields.CostField(default=0)
	repair_cost = uscs.CostPerSquareFootField()
	replacement_cost = uscs.CostPerSquareFootField()

	class Meta:
		abstract = True

	def __iter__(self):
		return iter([self])
