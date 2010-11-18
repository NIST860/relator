from django.db import models
from relator.database.models.base import Results, Cost
from relator.database.models.fields import DataLinkField
from relator.lighting import models as lighting
from relator.units import fields, dollar

class Lighting(Results, Cost):
	index = 'lighting'

	class Meta:
		abstract = True

	def takefrom(self, group, size, component):
		region = group.location.state.census_region
		rates = component.rates(region)
		index = lambda cost: group.index(cost, self.index)
		get = lambda attr: index(getattr(component, attr))

		self.new = index(component.cost * size)
		self.maintenance_cost = get('maintenance_cost')
		self.repair_cost = get('repair_cost') * size
		self.replacement_cost = get('replacement_cost') * size
		self.repair_rate = rates.repair
		self.replacement_rate = rates.replace

class DaylightSystem(Lighting):
	data = DataLinkField('ComponentBase', 'daylight_system')
	new = fields.CostField(default=0)
	old = 0 * dollar
	maintenance_cost = fields.CostField()
	repair_cost = fields.CostField()
	repair_rate = fields.YearField()
	replacement_cost = fields.CostField()
	replacement_rate = fields.YearField()

	def make(self, data):
		building = data.group.building
		systems = lighting.DaylightSystem.objects.order_by('fixtures')
		try:
			component = systems.filter(fixtures__gte=building.fixtures)[0]
		except IndexError:
			component = systems[-1]
		self.takefrom(data.group, building.square_feet, component)
		self.save()


class Overhang(Lighting):
	data = DataLinkField('ComponentBase', 'overhang')
	new = fields.CostField()
	old = 0 * dollar
	maintenance_cost = fields.CostField()
	repair_cost = fields.CostField()
	repair_rate = fields.YearField()
	replacement_cost = fields.CostField()
	replacement_rate = fields.YearField()
	index = 'weighted-average'

	def make(self, data):
		simulation = data.group.simulation
		standard = data.group.standard
		zone = data.group.location.climate_zone(standard)
		if not standard.use_overhang(zone): return
		size = simulation.overhang_area.into('ft**2')
		component = standard.overhang(zone)
		self.takefrom(data.group, size, component)
		self.save()
