from relator.utilities.decorators import cached_property
from relator.units import dollar
from relator.units.uscs import *
from base import Results, Cost, CostList
from mrr import Component, Components

class AssemblyComponent(Component):
	@cached_property
	def repair_cost(self):
		return self.component.repair_cost_for(
				self.building,
				self.data.heating_capacity.into('MBH'),
				self.data.cooling_capacity.into('cton'))

	@cached_property
	def replacement_cost(self):
		return self.component.replacement_cost_for(
				self.building,
				self.data.heating_capacity.into('MBH'),
				self.data.cooling_capacity.into('cton'))

	def __str__(self):
		return '%s %s' % (self.component, self.component.__class__._meta.verbose_name)


class AssemblyCost(Cost, Components):
	items = lambda self, master: (AssemblyComponent(component, self)
		for component in iter(self.assembly))

	def __init__(self, assembly, parent):
		self.assembly = assembly
		super(AssemblyCost, self).__init__(parent)

	@cached_property
	def new(self):
		return self.assembly.cost_for(
				self.building,
				self.data.heating_capacity.into('MBH'),
				self.data.cooling_capacity.into('cton'))

	@cached_property
	def old(self):
		return self.assembly.original_cost(self.building)


class AssemblyCostList(Components):
	indexer = 'HVAC'
	items = lambda self, master: (AssemblyCost(assembly, self)
		for assembly in filter(bool, (
			self.building.heating_system,
			self.building.cooling_system,
			self.building.packaged_unit,
			self.building.energy_supply)))
