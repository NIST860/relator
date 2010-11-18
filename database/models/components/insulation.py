from django.db import models
from itertools import chain
from quantities import ft
from relator.database.models.base import Results, Cost
from relator.database.models.fields import DataLinkField
from relator.units import fields, dollar, sum
from relator.insulation.models import (
		BlanketWallInsulation,
		RigidWallInsulation,
		RigidRoofInsulation)

def cost(insulation):
	return insulation.cost if insulation else (0 * (dollar / ft**2))


class Insulation(Results, Cost):
	class Meta:
		abstract = True

	def takefrom(self, group, sheets, size, *initial):
		sheets = list(sheets)
		index = lambda cost: group.index(cost, 'insulation')
		total = lambda attr: index(sum(getattr(sheet, attr) for sheet in sheets))
		self.maintenance_cost = total('maintenance_cost')
		self.repair_cost = total('repair_cost') * size
		self.replacement_cost = total('replacement_cost') * size
		self.new = total('cost') * size
		self.old = index(sum(map(cost, initial))) * size
		rates = self.RateModel.rates(group.location.state.census_region)
		self.repair_rate = rates.repair
		self.replacement_rate = rates.replace

	def make(self, data):
		location = data.group.location
		building = data.group.building
		standard = data.group.standard
		simulation = data.group.simulation
		return self.makewith(data, location, building, standard, simulation)


class WallInsulation(Insulation):
	data = DataLinkField('ComponentBase', 'wall_insulation')
	new = fields.CostField()
	old = fields.CostField()
	maintenance_cost = fields.CostField()
	repair_cost = fields.CostField()
	repair_rate = fields.YearField()
	replacement_cost = fields.CostField()
	replacement_rate = fields.YearField()
	RateModel = BlanketWallInsulation

	def makewith(self, data, location, building, standard, simulation):
		r = BlanketWallInsulation.r(standard, building, location.climate_zone(standard))
		inner = tuple(BlanketWallInsulation.sheets(location, building, standard))
		r -= sum((i.r for i in inner if i.r), 0)
		outer = RigidWallInsulation.sheets(location, building, standard, r)

		size = simulation.wall_area.into('ft**2')
		self.takefrom(data.group, chain(inner, outer), size,
				building.blanket_wall_insulation,
				building.rigid_wall_insulation)
		self.save()


class RoofInsulation(Insulation):
	data = DataLinkField('ComponentBase', 'roof_insulation')
	new = fields.CostField()
	old = fields.CostField()
	maintenance_cost = fields.CostField()
	repair_cost = fields.CostField()
	repair_rate = fields.YearField()
	replacement_cost = fields.CostField()
	replacement_rate = fields.YearField()
	RateModel = BlanketWallInsulation

	def makewith(self, data, location, building, standard, simulation):
		sheets = RigidRoofInsulation.sheets(location, building, standard)
		size = simulation.roof_area.into('ft**2')
		self.takefrom(data.group, sheets, size, building.roof_insulation)
		self.save()
