from relator.utilities.decorators import cache, cached_property
from relator.utilities.iter import irange
from relator.units import dollar, Quantity
from base import Cost, CostList


class ResidualValue(Cost):
	@cache
	def cost(self, index=True):
		if self.year > self.building.life: return 0 * dollar
		left = self.building.life - self.year
		total = (left / self.building.life) * self.master.first.cost(index)
		return self.adjust(total, index)

	@cache
	def delta(self, index=True):
		raise Exception('Change in residual cost unknown')


class BaseResidual(Cost):
	@cached_property
	def base(self):
		from relator.standards.models import Standard
		from relator.results import Results
		lowest = Standard.objects.order_by('year')[0]
		return Results(self.building, lowest, self.location, self.year, self.deflator, self.marr)

	@cache
	def cost(self, index=True):
		from relator.results.models import Base
		try:
			return Base.objects.get(
					set=self.master.set,
					building=self.building,
					location=self.location,
					period=self.year).residual
		except Base.DoesNotExist:
			return self.base.residual.cost()

	@cache
	def delta(self, index=True):
		raise Exception('Change in residual cost unknown')


class EnergyEfficiencyCost(CostList):
	items = lambda self, master: (master.assemblies, master.components)


class FirstCost(Cost):
	@cache
	def cost(self, index=True):
		subtotal = self.index(self.building.subtotal, index and 'weighted-average')
		delta = self.master.energy_efficiency.delta(index)
		return self.adjust(subtotal + delta, False)

	@cache
	def delta(self, index=True):
		return self.energy_efficiency.delta(index)


class FutureCost(CostList):
	present_value = True
	items = lambda self, master: (
			master.energy,
			master.mrr.base,
			master.mrr.maintenance,
			master.mrr.repair,
			master.mrr.replacement,
			master.mrr.credit,
			-(master.base_residual))


class InvestmentCost(CostList):
	items = lambda self, master: (master.first, -(master.base_residual), master.mrr.replacement)


class LifeCycleCost(CostList):
	items = lambda self, master: (master.first, master.future)
