from django.db import models
from base import Results
from relator.assemblies import models as assemblies
from relator.utilities.decorators import cached_property
from fields import DataLinkField
from relator.units import fields, sum
from relator.units.fields import metric

class Energy(Results):
	row = DataLinkField('Row', 'energy')
	use = metric.KiloWattHourField(null=True)
	cost = fields.CostField(null=True)
	fuels = assemblies.Fuel.objects.filter(name__in=('Gas', 'Electric'))

	def make(self, row):
		self.save()
		fuels = [Fuel.create(data=self, fuel=fuel) for fuel in self.fuels]
		self.use = sum(f.use for f in fuels)
		self.cost = sum(f.cost for f in fuels)
		self.save()

	@cached_property
	def usage(self):
		return dict((f.fuel, f.use) for f in self.fueldatas.all())


class Fuel(Results):
	data = models.ForeignKey(Energy, related_name='fueldatas')
	fuel = models.ForeignKey('assemblies.Fuel')
	cost = fields.CostField()
	use = metric.KiloWattHourField()

	def make(self, data, fuel):
		from relator.constants.models import Tariff, PriceIndex
		row = self.data.row
		year = row.period
		state = row.group.location.state
		deflator = float(row.group.database.deflator)
		enduses = row.group.simulation.fuel_enduses

		rate = Tariff.objects.get(fuel=self.fuel, state=state).tariff
		upv = PriceIndex.upv(self.fuel, state.census_region, year, deflator)

		self.use = enduses.get(fuel=self.fuel).total.into('kWh')
		self.cost = rate * upv * self.use
		self.save()
