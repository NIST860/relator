from itertools import chain
from django.db import models
from base import Results, Cost
from rates import Rates
from fields import DataLinkField
from relator.utilities.iter import irange
from relator.units import fields, dollar, sum

#########################################################
# Group Dependant

class AssemblyBase(Results):
	group = DataLinkField('Group', 'assemblies')
	cost = fields.CostField(null=True)
	delta = fields.CostField(null=True)

	def make(self, group):
		self.save()
		components = [AssemblyComponent.create(self, system) for system in filter(bool, (
			group.building.heating_system,
			group.building.cooling_system,
			group.building.packaged_unit,
			group.building.energy_supply))]
		self.cost = sum(c.cost for c in components)
		self.delta = sum(c.delta for c in components)
		self.save()


class AssemblyComponent(Results, Cost):
	assembly = models.ForeignKey(AssemblyBase, related_name='components')
	old = fields.CostField()
	new = fields.CostField()

	@classmethod
	def create(cls, assembly, system):
		self = cls(assembly=assembly)
		old = system.original_cost(assembly.group.building)
		new = system.cost_for(
				assembly.group.building,
				assembly.group.simulation.heating_capacity.into('MBH'),
				assembly.group.simulation.cooling_capacity.into('cton'))
		self.new = assembly.group.index(new, 'HVAC')
		self.old = assembly.group.index(old, 'HVAC')
		self.save()
		for part in system:
			AssemblyComponentPart.create(self, part).save()
		return self


class AssemblyComponentPart(Results):
	component = models.ForeignKey(AssemblyComponent, related_name='parts')
	maintenance_cost = fields.CostField()
	repair_cost = fields.CostField()
	repair_rate = fields.YearField()
	replacement_cost = fields.CostField()
	replacement_rate = fields.YearField()

	@classmethod
	def create(cls, component, part):
		self = cls(component=component)
		group = component.assembly.group
		args = (group.building,
				group.simulation.heating_capacity.into('MBH'),
				group.simulation.cooling_capacity.into('cton'))
		index = lambda cost: group.index(cost, 'HVAC')

		self.maintenance_cost = index(part.maintenance_cost)
		self.repair_cost = index(part.repair_cost_for(*args))
		self.replacement_cost = index(part.replacement_cost_for(*args))

		rates = part.rates(group.location.state.census_region)
		self.repair_rate = rates.repair
		self.replacement_rate = rates.replace
		self.save()
		return self


#########################################################
# Row Dependant

class Assembly(Results):
	row = DataLinkField('Row', 'assemblies')
	maintenance = fields.CostField(null=True)
	repair = fields.CostField(null=True)
	replacement = fields.CostField(null=True)
	credit = fields.CostField(null=True)

	def make(self, row):
		self.save()
		components = row.group.assemblies.components.all()
		parts = chain(*(c.parts.all() for c in components))
		totals = [AssemblyPartTotals.create(p, parent=self) for p in parts]
		self.maintenance = sum(t.maintenance for t in totals)
		self.repair = sum(t.repair for t in totals)
		self.replacement = sum(t.replacement for t in totals)
		self.credit = sum(t.credit for t in totals)
		self.save()


class AssemblyPartTotals(Rates):
	parent = models.ForeignKey(Assembly, related_name='totals')
	maintenance = fields.CostField()
	repair = fields.CostField()
	replacement = fields.CostField()
	credit = fields.CostField()
