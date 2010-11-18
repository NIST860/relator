from django.db import models
from relator.database.models.base import Results, Cost
from relator.units import fields
from relator.windows.models import WindowComponent, Direction

class Window(Results, Cost):
	data = models.ForeignKey('ComponentBase', related_name='windows')
	direction = models.ForeignKey(Direction, primary_key=True)
	new = fields.CostField()
	old = fields.CostField()
	maintenance_cost = fields.CostField()
	repair_cost = fields.CostField()
	repair_rate = fields.YearField()
	replacement_cost = fields.CostField()
	replacement_rate = fields.YearField()

	def make(self, data, direction):
		building = data.group.building
		simulation = data.group.simulation
		region = data.group.location.state.census_region
		component = WindowComponent(building.window, simulation.windows.get(direction=direction))

		index = lambda cost: data.group.index(cost, 'windows')
		get = lambda attr: index(getattr(component, attr))

		self.new = index(component.cost * component.size)
		self.old = index(component.old.cost * component.size)

		self.maintenance_cost = get('maintenance_cost')
		self.repair_cost = get('repair_cost') * component.size
		self.replacement_cost = get('replacement_cost')
		rates = component.rates(region)
		self.repair_rate = rates.repair
		self.replacement_rate = rates.replace
		self.save()
