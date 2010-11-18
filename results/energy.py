from relator.units import dollar, sum
from relator.assemblies.models import Fuel
from relator.constants.models import PriceIndex, Tariff
from relator.utilities.decorators import cached_property, cache
from base import Cost, CostList

class FuelCost(Cost):
	def __init__(self, fuel, parent):
		self.fuel = fuel
		super(FuelCost, self).__init__(parent)

	@cached_property
	def new(self):
		return self.rate * self.upv * self.use.into('kWh')

	@cached_property
	def old(self):
		raise Exception('Old fuel rates are unknown')

	@cached_property
	def rate(self):
		return Tariff.objects.get(fuel=self.fuel, state=self.location.state).tariff

	@cached_property
	def upv(self):
		return PriceIndex.upv(self.fuel, self.master.census_region, self.year, self.deflator)

	@cached_property
	def use(self):
		return self.data.fuel_enduses.get(fuel=self.fuel).total.into(self.fuel.units or 'kWh')


class EnergyCost(CostList):
	items = lambda self, master: (FuelCost(fuel, self)
		for fuel in Fuel.objects.filter(name__in=('Gas', 'Electric')))

	def fuel(self, name):
		for fc in self:
			if fc.fuel.name.lower() == name.lower():
				return fc

	def use(self):
		return sum(i.use for i in self)

	@cached_property
	def usage(self):
		return dict((fc.fuel, fc.use) for fc in self)
