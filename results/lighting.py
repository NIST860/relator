from relator.utilities.decorators import cache, cached_property
from relator.lighting.models import DaylightSystem
from relator.units import dollar
from quantities import ft
from base import Cost, CostList
from mrr import Component, Components

class DaylightingCost(Component):
	size = property(lambda self: self.building.square_feet)
	indexer = 'lighting'
	old = 0 * dollar

	def __init__(self, parent):
		if not parent.master.standard.use_daylighting:
			return super(DaylightingCost, self).__init__(None, parent)
		systems = DaylightSystem.objects.order_by('fixtures')
		try:
			component = systems.filter(fixtures__gte=parent.master.building.fixtures)[0]
		except IndexError:
			component = systems[-1]
		return super(DaylightingCost, self).__init__(component, parent)

	@cached_property
	def new(self):
		return (self.component.cost * self.size) if self.component else 0 * dollar


class OverhangCost(Component):
	size = property(lambda self: self.data.overhang_area.into('ft**2'))
	indexer = 'weighted-average'
	old = 0 * dollar

	def __init__(self, parent):
		super(OverhangCost, self).__init__(
				parent.master.standard.overhang(parent.master.climate_zone), parent)

	@cached_property
	def new(self):
		return (self.component.cost * self.size) if self.component else 0 * dollar


class LightingCost(Components):
	children = {'daylighting': DaylightingCost, 'overhang': OverhangCost}
