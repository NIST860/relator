from new import instancemethod
from relator.utilities.decorators import cache
from itertools import chain
from relator.units import dollar, sum
from quantities import Quantity
from utilities import do

class Results(object):
	indexer, present_value = None, False
	
	def __init__(self, parent):
		self.parent = parent
		self.master = parent.master
		self.building = parent.building
		self.location = parent.location
		self.standard = parent.standard
		self.data = parent.data
		self.year = parent.year
		self.deflator = parent.deflator
		self.marr = parent.marr

	def spv(self, t=None):
		t = t or self.year
		if isinstance(t, Quantity):
			t.units = 'year'
			t = t.item()
		return 1 / ((1 + self.deflator) ** t)

	def upv(self, t=None):
		t = t or self.year
		if isinstance(t, Quantity):
			t.units = 'year'
			t = int(t.item())
		return sum(self.spv(y) for y in range(t))

	@cache
	def adjust(self, cost, index, pv=False, year=None):
		year = year or self.year
		if index: cost = self.index(cost)
		if pv or self.present_value: cost = self.pv(cost, year)
		return cost

	@cache
	def index(self, cost, indexer=None):
		indexer = indexer or self.indexer
		if not indexer: return cost
		return cost * self.location.indicies.get(index__pk=indexer).value

	@cache
	def pv(self, cost, year=None):
		return cost * self.spv(year)

	def __str__(self):
		return self.__class__.__name__


class Cost(Results):
	@cache
	def cost(self, index=True):
		return self.adjust(self.new, index)

	@cache
	def delta(self, index=True):
		return self.adjust(self.new - self.old, index)

	def __neg__(self):
		return NegativeCost(self)


class ResultList(Results):
	items, children = lambda self, master: (), {}

	def __init__(self, parent):
		super(ResultList, self).__init__(parent)
		for (name, cls) in self.children.items():
			setattr(self, name, cls(self))

	def __iter__(self):
		if not hasattr(self, '__iter'):
			self.__iter = list(chain(
				self.items(self.master),
				(getattr(self, key) for key in self.children)))
		return iter(self.__iter)


class CostList(ResultList):
	@cache
	def cost(self, index=True):
		cost = sum(item.cost(index) for item in self)
		return self.adjust(cost, index)

	@cache
	def delta(self, index=True):
		delta = sum(item.delta(index) for item in self)
		return self.adjust(delta, index)

	def __neg__(self):
		return NegativeCost(self)


class AltCostList(ResultList):
	@cache
	def cost(self, index=True):
		return sum(getattr(item, self.field)(index) for item in self)

	@cache
	def delta(self, index=True):
		raise Exception('Can not find delta of %s' % self)

	def __neg__(self):
		return NegativeCost(self)


class NegativeCost(object):
	def __init__(self, cost):
		self.parent = cost

	def cost(self, *args, **kwargs):
		return -(self.parent.cost(*args, **kwargs))

	def delta(self, *args, **kwargs):
		return -(self.parent.delta(*args, **kwargs))

	def __neg__(self):
		return self.parent
