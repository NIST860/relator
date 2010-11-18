from decimal import Decimal
from relator.units import Quantity
from relator.zones.models import Ashrae01, Ashrae04
from relator.data.models import EnergyPlusData
from relator.utilities.decorators import cache, cached_property
from relator.standards.models import Standard
from energy import EnergyCost
from assemblies import AssemblyCostList
from components import ComponentCostList
from mrr import MRR
from models import ResultSet
from other import (
		ResidualValue,
		BaseResidual,
		EnergyEfficiencyCost,
		FirstCost,
		FutureCost,
		InvestmentCost,
		LifeCycleCost)
from carbon import Emissions

class Results(object):
	def __init__(self, building, standard, location, year, carbon, deflator, marr=None):
		self.master = self
		self.building = building
		self.location = location
		self.standard = standard
		self.year = year if isinstance(year, Quantity) else Quantity(year, 'years')
		self.data = EnergyPlusData.objects.get(building=building, location=location, standard=standard)
		self.deflator = float(deflator)
		self.marr = float(marr or deflator)

		try:
			self.set = ResultSet.objects.get(
					deflator=Decimal(str(deflator)),
					marr=Decimal(marr or str(deflator)))
		except ResultSet.DoesNotExist:
			self.set = None

		self.components = ComponentCostList(self)
		self.assemblies = AssemblyCostList(self)
		self.energy = EnergyCost(self)
		self.mrr = MRR(self)
		self.base_residual = BaseResidual(self)
		self.residual = ResidualValue(self)
		self.energy_efficiency = EnergyEfficiencyCost(self)
		self.first = FirstCost(self)
		self.future = FutureCost(self)
		self.investment = InvestmentCost(self)
		self.lifecycle = LifeCycleCost(self)

		self.emissions = Emissions(self, carbon)

	@cached_property
	def years(self):
		return range(int(self.year.item()))

	@cached_property
	def census_region(self):
		return self.location.state.census_region

	@cached_property
	def climate_zone(self):
		type = self.standard.zone_type.model_class()
		if type == Ashrae01:
			return self.location.ashrae01
		elif type == Ashrae04:
			return self.location.ashrae04
		raise ValueError('Can not determine climate zone for standard %s' % self.standard)

	@cache
	def airr(self, base):
		si = self.investment.cost()
		bi = base.investment.cost()
		if si <= bi: return 'Infinite'
		sec = self.energy.cost()
		bec = base.energy.cost()
		sir = ((sec - bec) / (si - bi)).item()
		if sir < 0: return 'Imaginary'
		n, r = self.year.item(), self.marr
		return (1 + r) * (sir ** (1.0 / n)) - 1
