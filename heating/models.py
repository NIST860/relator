from django.db import models
from django.db.models import Count
from django.contrib.humanize.templatetags.humanize import intcomma

from relator.assemblies import models as base
from relator.zones.models import CensusRegion as Zone

from relator.units import fields, dollar, sum
from relator.units.fields import uscs
from relator.units.uscs import MBH

from relator.utilities.models import Type
from relator.utilities.decorators import cached_property
from relator.utilities.templatetags.utils import price

#####################################
# Boilers
#####################################

class BoilerFlow(Type):
	pass


class Boiler(models.Model):
	number = models.CharField(max_length=15)
	description = models.CharField(max_length=255)
	fuels = models.ManyToManyField(base.Fuel)
	flow = models.ForeignKey(BoilerFlow, blank=True, null=True)
	mbh = uscs.MBHField()
	cost = fields.CostField()

	class Meta:
		ordering = 'mbh',

	@property
	def cost_per_mbh(self):
		return self.cost / self.mbh

	def matching(self, objects, fueled=False):
		if not fueled: return objects
		objects = objects.annotate(num=Count('fuels'))
		objects = objects.filter(num=self.fuels.count())
		hasfuel = lambda set, fuel: set.filter(fuels=fuel)
		return reduce(hasfuel, self.fuels.all(), objects)

	def bestfit(self, objects, fueled=False):
		for item in self.matching(objects, fueled):
			if item.contains(self.mbh):
				return item

	def maintenance_cost_for(self, building, mbh, tons):
		return self.maintenance_cost

	def repair_cost_for(self, building, mbh, tons):
		return self.repair_cost * mbh

	def replacement_cost_for(self, building, mbh, tons):
		return self.replacement_cost * mbh

	@cached_property
	def repair_cost(self):
		return self.bestfit(BoilerRepair.objects, True).cost

	@cached_property
	def maintenance_cost(self):
		return self.bestfit(BoilerMaintenance.objects.filter(flow=self.flow)).cost

	@cached_property
	def replacement_cost(self):
		try:
			cost = self.replacements.all()[0].cost
		except IndexError:
			cost = self.cost
		return cost / self.mbh

	def rates(self, zone):
		return self.matching(BoilerRates.objects, True).get(zone=zone)

	def __unicode__(self):
		fuels = '/'.join(map(str, self.fuels.all()))
		return '%.2f MBH, %s %s boiler' % (self.mbh, price(self.cost), fuels)


class Upkeep(models.Model):
	min = uscs.MBHField()
	max = uscs.MBHField(blank=True, null=True, help_text='Leave blank for none.')

	class Meta:
		abstract = True
		ordering = 'cost',

	def contains(self, mbh):
		return self.min <= mbh <= (self.max or mbh)

	def __unicode__(self):
		if self.max:
			return '%s to %s: %s' % (self.min, self.max, self.cost)
		return 'More than %s: %s' % (self.min, self.cost)


class BoilerMaintenance(Upkeep):
	flow = models.ForeignKey(BoilerFlow, blank=True, null=True)
	cost = fields.CostField()

	class Meta:
		ordering = 'flow', 'cost'

	def __unicode__(self):
		return super(BoilerMaintenance, self).__unicode__() + ' (%s)' % (self.flow or 'Electric')


class BoilerRepair(Upkeep):
	mbh = uscs.MBHField()
	fuels = models.ManyToManyField(base.Fuel)
	cost = uscs.CostPerMBHField()

	@cached_property
	def cost_per_mbh(self):
		return self.cost / self.mbh

	def adjusted_cost(self, mbh):
		return self.cost_per_mbh * mbh

	def __unicode__(self):
		fuels = '/'.join(map(str, self.fuels.all()))
		return super(BoilerRepair, self).__unicode__() + ' (%s)' % fuels


class BoilerReplace(models.Model):
	unit = models.ForeignKey(Boiler, related_name='replacements')
	cost = fields.CostField()

	class Meta:
		ordering = 'cost',

	def __unicode__(self):
		return '%s: %s' % (self.unit, price(self.cost))


class BoilerRates(models.Model):
	fuels = models.ManyToManyField(base.Fuel)
	zone = models.ForeignKey(Zone)
	repair = fields.YearField()
	replace = fields.YearField()

	class Meta:
		verbose_name_plural = 'rate sets'
		ordering = 'zone',

	def __unicode__(self):
		fuels = '/'.join(map(str, self.fuels.all()))
		return 'Rates for %s boilers in zone %s' % (fuels, self.zone)


#####################################
# Systems
#####################################

class EnergySupply(models.Model):
	number = models.CharField(max_length=15)
	description = models.CharField(max_length=255)
	mbh = uscs.MBHField()
	cost = fields.CostField(help_text='Boiler cost not included')
	square_feet = uscs.SquareFootField()
	boilers = models.ManyToManyField(Boiler)

	class Meta:
		ordering = 'mbh',
		verbose_name_plural = 'energy supplies'

	def __iter__(self):
		return iter(self.boilers.all())

	@property
	def cost_per_mbh(self):
		return self.cost / self.mbh

	@cached_property
	def fixed_cost_per_square_foot(self):
		return self.cost / self.square_feet

	def fixed_cost(self, building):
		return self.fixed_cost_per_square_foot * building.square_feet

	def cost_for(self, building, mbh, tons):
		mbh = mbh.into(MBH)
		cost_per_mbh = sum(boiler.cost_per_mbh for boiler in self.boilers.all())
		return (cost_per_mbh * mbh) + self.fixed_cost(building)

	def original_cost(self, building):
		return self.cost_for(building, self.mbh, None)

	def __unicode__(self):
		return u'%s ft\u00B2, %.2f MBH, %s unit' % (intcomma(self.square_feet.just('ft**2')), self.mbh, price(self.cost))


class HeatingSystem(models.Model):
	number = models.CharField(max_length=15)
	boiler = models.ForeignKey(Boiler)
	(a, b) = (548.45, -.366)

	def __iter__(self):
		return iter([self.boiler])

	def marginal_cost(self, mbh):
		mbh = mbh.just(MBH)
		return (self.a * (mbh ** self.b)) * (dollar / MBH)

	def cost_for(self, building, mbh, tons):
		return self.marginal_cost(mbh) * mbh

	def original_cost(self, building):
		return self.cost_for(building, self.boiler.mbh, None)

	def __unicode__(self):
		return 'Heat system with %s' % self.boiler
