from relator.windows.models import ASHRAEWindow, WindowModifier, Direction
from relator.windows.models import WindowComponent as ModelComponent
from relator.utilities.decorators import cache, cached_property
from relator.units import dollar
from quantities import ft
from base import Cost, CostList
from mrr import Component, Components

class WindowComponent(Component):
	size = property(lambda self: self.component.size)

	def __init__(self, direction, parent):
		self.direction = direction
		super(WindowComponent, self).__init__(ModelComponent(
				parent.building.window,
				parent.data.windows.get(direction=direction)), parent)

	def __str__(self):
		return '%s: %s' % (self.direction, self.component)

	@cached_property
	def new(self):
		return self.component.cost * self.component.size

	@cached_property
	def old(self):
		return self.component.old.cost * self.component.size


class WindowCost(Components):
	indexer = 'windows'
	items = lambda self, master: list(WindowComponent(direction, self)
			for direction in Direction.objects.order_by('pk'))
