from django.db import models
from itertools import chain
from relator.database.models.base import Results
from relator.database.models.fields import DataLinkField
from windows import Window
from relator.windows.models import Direction
from relator.units import fields, sum

class ComponentBase(Results):
	group = DataLinkField('Group', 'components')
	cost = fields.CostField(null=True)
	delta = fields.CostField(null=True)

	def make(self, group):
		self.save()
		for d in Direction.objects.all():
			Window.create(data=self, direction=d)
		parts = list(self.parts())
		self.cost = sum(p.cost for p in parts)
		self.delta = sum(p.delta for p in parts)
		self.save()

	def parts(self):
		standard = self.group.standard
		zone = self.group.location.climate_zone(standard)

		for window in self.windows.all():
			yield window
		if standard.use_overhang(zone):
			yield self.overhang
		if standard.use_daylighting:
			yield self.daylight_system
		yield self.wall_insulation
		yield self.roof_insulation
