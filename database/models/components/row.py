from django.db import models
from relator.database.models.base import Results
from relator.database.models.rates import Rates
from relator.database.models.fields import DataLinkField
from relator.units import fields, sum

class Component(Results):
	row = DataLinkField('Row', 'components')
	maintenance = fields.CostField(null=True)
	repair = fields.CostField(null=True)
	replacement = fields.CostField(null=True)
	credit = fields.CostField(null=True)

	def make(self, row):
		self.save()
		parts = row.group.components.parts()
		totals = [ComponentTotals.create(p, parent=self) for p in parts]
		self.maintenance = sum(t.maintenance for t in totals)
		self.repair = sum(t.repair for t in totals)
		self.replacement = sum(t.replacement for t in totals)
		self.credit = sum(t.credit for t in totals)
		self.save()


class ComponentTotals(Rates):
	parent = models.ForeignKey(Component, related_name='totals')
	maintenance = fields.CostField()
	repair = fields.CostField()
	replacement = fields.CostField()
	credit = fields.CostField()
