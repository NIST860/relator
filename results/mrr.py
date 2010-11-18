from itertools import chain
from relator.units import dollar, sum
from relator.utilities.iter import irange
from relator.utilities.decorators import cache, cached_property
from base import Cost, CostList, AltCostList

class Component(Cost):
	@cached_property
	def maintenance_cost(self):
		return self.component.maintenance_cost

	@cached_property
	def repair_cost(self):
		return self.component.repair_cost * self.size

	@cached_property
	def replacement_cost(self):
		return self.component.replacement_cost * self.size

	@cached_property
	def rates(self):
		return self.component.rates

	def __init__(self, component, parent):
		self.component = component
		super(Component, self).__init__(parent)

	@cache
	def maintenance(self, index=True):
		if not self.component: return 0 * dollar
		self.year.units = 'year'
		year = self.year.item()
		result = self.maintenance_cost * year
		return self.adjust(result, index, True)

	@cache
	def repair(self, index=True):
		if not self.component: return 0 * dollar
		self.year.units = 'year'
		year = int(self.year.item())
		rates = self.rates(self.master.census_region)
		repair, replace = rates.repair, rates.replace
		cost = 0 * dollar
		replaced = 1
		for year in irange(1, year):
			if (year - replaced) >= replace:
				replaced = year
			if (year - replaced) >= repair:
				cost += self.adjust(self.repair_cost, index, True, year)
		return cost

	@cache
	def replacement(self, index=True):
		if not self.component: return 0 * dollar
		rate = self.rates(self.master.census_region).replace
		cost = self.replacement_cost
		times = int((self.year // rate).item())
		return sum(self.adjust(cost, index, True, rate * i) for i in irange(1, times))

	@cache
	def credit(self, index=True):
		if not self.component: return 0 * dollar
		rate = self.rates(self.master.census_region).replace
		self.year.units = 'year'
		if self.year < rate: return 0 * dollar
		leftover = self.year % rate
		result = (leftover / rate) * self.replacement_cost
		return self.adjust(result, index, True)

	__str__ = lambda self: str(self.component)
	__unicode__ = lambda self: unicode(self.component)


class Components(CostList):
	@cache
	def maintenance(self, index=True):
		return sum(item.maintenance(index) for item in self)

	@cache
	def repair(self, index=True):
		return sum(item.repair(index) for item in self)

	@cache
	def replacement(self, index=True):
		return sum(item.replacement(index) for item in self)

	@cache
	def credit(self, index=True):
		return sum(item.credit(index) for item in self)


class Maintenance(AltCostList):
	items = lambda self, master: (master.components, master.assemblies)
	field = 'maintenance'


class Repair(AltCostList):
	items = lambda self, master: (master.components, master.assemblies)
	field = 'repair'


class Replacement(AltCostList):
	items = lambda self, master: (master.components, master.assemblies)
	field = 'replacement'


class Credit(AltCostList):
	items = lambda self, master: (master.components, master.assemblies)
	field = 'credit'


class Base(Cost):
	indexer = 'whitestone'

	@cache
	def cost(self, index=True):
		self.year.units = 'year'
		years = irange(1, int(self.year.item()))
		area = self.building.square_feet
		cost = lambda year: self.building.costs.get(year=year).cost
		total = area * sum(cost(year) * self.spv(year) for year in years)
		return self.index(total) if index else total

	@cache
	def delta(self, index=True):
		raise Exception('Change in Base MRR costs is unknown')


class MRR(CostList):
	children = {
		'base': Base,
		'maintenance': Maintenance,
		'repair': Repair,
		'replacement': Replacement,
		'credit': Credit,
	}
