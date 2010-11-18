from relator.insulation.models import (
		BlanketWallInsulation,
		RigidWallInsulation,
		RigidRoofInsulation)
from relator.units import dollar
from relator.utilities.decorators import cached_property, cache
from quantities import ft
from base import Cost, CostList
from mrr import Component, Components


class SheetCost(Component):
	size = property(lambda self: self.parent.size)
	new = property(lambda self: self.component.cost * self.size)
	old = 0 * dollar


class SheetCostList(Components):
	indexer = 'insulation'

	def next(self, options, r):
		try:
			return options.order_by('-r').filter(r__lte=r)[0]
		except IndexError:
			return options.order_by('r')[0]

	def _cost(self, insulation):
		return insulation.cost if insulation else (0 * (dollar / ft**2))


class WallInsulationCost(SheetCostList):
	wall = property(lambda self: self.building.wall)

	@cached_property
	def r(self):
		return self.standard.wall_r(self.wall, self.master.climate_zone)

	@cached_property
	def size(self):
		return self.data.wall_area.into('ft**2')

	def items(self, master):
		options = BlanketWallInsulation.oftype(master.building.blanket_wall_insulation)
		next = self.next(options, self.r)
		insulations = [next]
		r = self.r - (next.r or 0)
		options = RigidWallInsulation.oftype(master.building.rigid_wall_insulation)
		while r > 0:
			next = self.next(options, r)
			if next.r is None: break
			insulations.append(next)
			r -= next.r
		sheets = filter(lambda i: i.r, insulations)
		return (SheetCost(sheet, self) for sheet in sheets)

	@cached_property
	def old(self):
		return sum(map(self._cost, (
			self.building.blanket_wall_insulation,
			self.building.rigid_wall_insulation)))


class RoofInsulationCost(SheetCostList):
	roof = property(lambda self: self.building.roof)

	@cached_property
	def r(self):
		return self.standard.roof_r(self.roof, self.master.climate_zone)

	@cached_property
	def size(self):
		return self.data.roof_area.into('ft**2')

	def items(self, master):
		r, insulations = self.r, []
		options = RigidRoofInsulation.oftype(self.building.roof_insulation)
		while r > 0:
			next = self.next(options, r)
			if next.r is None: break
			insulations.append(next)
			r -= next.r
		sheets = filter(lambda i: i.r, insulations)
		return (SheetCost(sheet, self) for sheet in sheets)

	@cached_property
	def old(self):
		return self._cost(self.building.roof_insulation)


class InsulationCost(Components):
	children = {'wall': WallInsulationCost, 'roof': RoofInsulationCost}
