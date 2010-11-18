from django.db import models
from quantities import year

from relator.assemblies import models as base
from relator.cooling import models as cooling
from relator.heating import models as heating
from relator.zones.models import CensusRegion as Zone

from relator.units import dollar, fields
from relator.units.uscs import MBH
from relator.units.fields import uscs

from relator.utilities.models import Type
from relator.utilities.decorators import cached_property
from relator.utilities.templatetags.utils import price

#####################################
# Types
#####################################

class SystemType(Type):
	""" Split System, Self-Contained System, Heat Pump, etc. """

#####################################
# System
#####################################

class PackagedUnit(models.Model):
	number = models.CharField(max_length=15)
	description = models.CharField(max_length=255)
	type = models.ForeignKey(SystemType)
	flow = models.ForeignKey(base.Flow, blank=True, null=True)
	vav = models.BooleanField()
	dx = models.BooleanField()
	multizone = models.BooleanField()
	tons = uscs.TonField()
	mbh = uscs.MBHField(blank=True, null=True, help_text='Leave blank if there is no heating system.')
	cost = fields.CostField()

	class Meta:
		ordering = 'tons',

	@property
	def cost_per_mbh(self):
		return self.cost / self.mbh

	@property
	def cost_per_ton(self):
		return self.cost / self.tons

	def cost_for(self, building, mbh, tons):
		ccost = self.cost_per_ton * tons
		if mbh is None or self.mbh is None:
			return ccost
		hcost = self.cost_per_mbh * mbh
		return max(hcost, ccost)

	def original_cost(self, building):
		return self.cost_for(building, self.mbh, self.tons)

	###########
	# Helpers #
	###########

	def bestfit(self, objects):
		for item in objects.filter(flow=self.flow, type=self.type):
			if item.contains(self.tons):
				return item

	def typefit(self, objects):
		if self.vav:
			return objects.filter(vav=True, multizone=self.multizone)
		elif self.dx:
			return objects.filter(vav=False, dx=True)
		return objects.filter(vav=False, dx=False, multizone=self.multizone)

	@cached_property
	def furnace_component(self):
		return FurnaceComponent(self, base.Fuel.objects.get(name='Gas'))

	##############################
	# Maintenance/Repair/Replace #
	##############################

	def __iter__(self):
		return iter([self, self.furnace_component])

	def maintenance_cost_for(self, building, mbh, tons):
		return self.maintenance_cost

	def repair_cost_for(self, building, mbh, tons):
		return self.repair_cost * tons

	def replacement_cost_for(self, building, mbh, tons):
		return self.replacement_cost * tons

	########################
	# Main Costs and Rates #
	########################

	@cached_property
	def maintenance_cost(self):
		return self.bestfit(Maintenance.objects).cost

	@cached_property
	def repair_cost(self):
		for repair in self.typefit(Repair.objects):
			if repair.contains(self.tons):
				return repair.cost_per_ton

	@cached_property
	def replacement_cost(self):
		try:
			cost = self.replacements.all()[0].cost
		except self.replacements.model.DoesNotExist:
			cost = self.cost
		return cost / self.tons

	def rates(self, zone):
		return self.typefit(Rates.objects).get(zone=zone)

	###########################

	def __unicode__(self):
		power = '{0} ton'.format(self.tons.item())
		if self.mbh: power += ', {0}'.format(self.mbh)
		type = '{1} {0}'.format(self.flow, self.type) if self.flow else unicode(self.type)
		return '%s, %s %s unit' % (power, price(self.cost), type)


#####################################
# Main Costs
#####################################

class Maintenance(cooling.Upkeep):
	flow = models.ForeignKey(base.Flow, related_name='packaged_maintenance_set')
	type = models.ForeignKey(SystemType)

	class Meta:
		ordering = 'flow', 'type', 'cost'


class Repair(cooling.Upkeep):
	vav = models.BooleanField()
	dx = models.BooleanField()
	multizone = models.BooleanField()
	tons = uscs.TonField()

	class Meta:
		ordering = 'vav', 'dx', 'multizone', 'cost'

	@property
	def cost_per_ton(self):
		return self.cost / self.tons


class Replace(models.Model):
	unit = models.ForeignKey(PackagedUnit, related_name='replacements')
	cost = fields.CostField()

	class Meta:
		verbose_name_plural = 'replacements'

	def __unicode__(self):
		return '%s: %s' % (self.unit, price(self.cost))

#####################################
# Heating Costs
#####################################

class FurnaceUpkeep(heating.Upkeep):
	fuel = models.ForeignKey(base.Fuel)
	cost = fields.CostField()
	mbh = uscs.MBHField()

	class Meta:
		abstract = True

	@cached_property
	def cost_per_mbh(self):
		return self.cost / self.mbh

	def adjusted_cost(self, mbh):
		return self.cost_per_mbh * mbh


class FurnaceRepair(FurnaceUpkeep):
	pass


class FurnaceReplace(FurnaceUpkeep):
	class Meta:
		verbose_name_plural = 'furnace replacements'


class FurnaceComponent(object):
	def __init__(self, system, fuel):
		self.system, self.fuel = system, fuel

	__str__ = __unicode__ = lambda self: 'Furnace for %s' % self.system

	def bestfit(self, objects):
		for item in objects.filter(fuel=self.fuel):
			if item.contains(self.system.mbh):
				return item

	def maintenance_cost_for(self, building, mbh, tons):
		return self.maintenance_cost

	def repair_cost_for(self, building, mbh, tons):
		return self.repair_cost * mbh

	def replacement_cost_for(self, building, mbh, tons):
		return self.replacement_cost * mbh

	@cached_property
	def maintenance_cost(self):
		return 0 * dollar

	@cached_property
	def repair_cost(self):
		if not self.system.mbh: return 0 * dollar / MBH
		return self.bestfit(FurnaceRepair.objects).cost_per_mbh

	@cached_property
	def replacement_cost(self):
		if not self.system.mbh: return 0 * dollar / MBH
		return self.bestfit(FurnaceReplace.objects).cost_per_mbh

	def rates(self, zone):
		if not self.system.mbh:
			return FurnaceRates(
					fuel=self.fuel,
					zone=zone,
					repair=100 * year,
					replace=100 * year)
		return FurnaceRates.objects.get(fuel=self.fuel, zone=zone)

#####################################
# Rates
#####################################

class Rates(models.Model):
	vav = models.BooleanField(default=False)
	dx = models.BooleanField(default=False)
	multizone = models.BooleanField(default=False)
	zone = models.ForeignKey(Zone, related_name='packagedunit_rates_set')
	repair = fields.YearField()
	replace = fields.YearField()

	class Meta:
		unique_together = 'vav', 'dx', 'multizone', 'zone'
		verbose_name_plural = 'rate sets'
		ordering = 'vav', 'dx', 'multizone', 'zone'

	def __unicode__(self):
		return 'Rates in zone %s' % self.zone


class FurnaceRates(models.Model):
	fuel = models.ForeignKey(base.Fuel)
	zone = models.ForeignKey(Zone)
	repair = fields.YearField()
	replace = fields.YearField()

	class Meta:
		unique_together = 'fuel', 'zone'
		verbose_name_plural = 'furnace rate sets'
		ordering = 'fuel', 'zone'

	def __unicode__(self):
		return 'Rates for %s furnaces in zone %s' % (self.fuel, self.zone)
