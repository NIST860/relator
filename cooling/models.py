from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.humanize.templatetags.humanize import intcomma

from relator.assemblies import models as base
from relator.zones.models import CensusRegion as Zone

from relator.units import fields, dollar, sum
from relator.units.uscs import cooling
from relator.units.fields import uscs

from relator.utilities.models import Type
from relator.utilities.decorators import cached_property
from relator.utilities.templatetags.utils import price

#####################################
# Types
#####################################

class SystemType(Type):
	""" Centrifugal, Scroll, Absorption, etc. """

#####################################
# Abstract Base Classes
#####################################

def components():
	components = FanCoil, Chiller, CoolingTower
	cs = map(ContentType.objects.get_for_model, components)
	return (c.pk for c in cs)


class Component(models.Model):
	number = models.CharField(max_length=15)
	description = models.CharField(max_length=255)
	cost = fields.CostField()
	tons = uscs.TonField()

	class Meta:
		abstract = True

	@classmethod
	def rates(cls, zone):
		type = ContentType.objects.get_for_model(cls)
		return Rates.objects.get(component=type, zone=zone)

	@cached_property
	def cost_per_ton(self):
		return self.cost / self.ton

	def average_cost(self, tons):
		return self.marginal_cost(tons) * tons

	def marginal_cost(self, tons):
		tons = tons.just(cooling)
		return (self.a * (tons ** self.b)) * (dollar / cooling)

	def bestfit(self, set):
		for item in set:
			if item.contains(self.tons):
				return item

	def maintenance_cost_for(self, building, mbh, tons):
		return self.maintenance_cost

	def repair_cost_for(self, building, mbh, tons):
		return self.repair_cost * tons

	def replacement_cost_for(self, building, mbh, tons):
		return self.replacement_cost * tons

	@cached_property
	def maintenance_cost(self):
		return self.bestfit(self.maintenances.objects.all()).cost

	@cached_property
	def repair_cost(self):
		return self.bestfit(self.repairs.objects.all()).cost_per_ton

	@cached_property
	def replacement_cost(self):
		try:
			cost = self.replacements.all()[0].cost
		except IndexError:
			cost = self.cost
		return cost / self.tons

	def __unicode__(self):
		return '%.2f ton, %s' % (self.tons, price(self.cost))


class Upkeep(models.Model):
	min = uscs.TonField()
	max = uscs.TonField(blank=True, null=True, help_text='Leave blank for none.')
	cost = fields.CostField()

	class Meta:
		abstract = True
		ordering = 'cost',

	def contains(self, tons):
		return self.min <= tons <= (self.max or tons)

	def __unicode__(self):
		if self.max:
			return '%s to %s tons: %s' % (self.min, self.max, price(self.cost))
		return 'More than %s tons: %s' % (self.min, price(self.cost))


class Maintenance(Upkeep):
	class Meta:
		abstract = True


class Repair(Upkeep):
	tons = uscs.TonField()

	class Meta:
		abstract = True

	@property
	def cost_per_ton(self):
		return self.cost / self.tons


class Replace(models.Model):
	cost = fields.CostField()

	class Meta:
		abstract = True
		ordering = 'cost',

	def __unicode__(self):
		return '%s: %s' % (self.unit, price(self.cost))

#####################################
# Components
#####################################

#############
# Fan Coils #
#############

class FanCoilRepair(Repair):
	pass


class FanCoilMaintenance(Maintenance):
	pass


class FanCoil(Component):
	repairs = FanCoilRepair
	maintenances = FanCoilMaintenance
	(a, b) = (1093.9, -0.552)


class FanCoilReplace(Replace):
	unit = models.ForeignKey(FanCoil, related_name='replacements')

	class Meta(Replace.Meta):
		verbose_name_plural = 'fan coil replacements'

############
# Chillers #
############

class ChillerRepair(Repair):
	flow = models.ForeignKey(base.Flow)
	type = models.ForeignKey(SystemType)

	class Meta:
		ordering = 'type', 'flow'

	def __unicode__(self):
		return super(ChillerRepair, self).__unicode__() + ' (%s %s)' % (self.flow, self.type)


class ChillerMaintenance(Maintenance):
	flow = models.ForeignKey(base.Flow)
	type = models.ForeignKey(SystemType)

	class Meta:
		ordering = 'type', 'flow'

	def __unicode__(self):
		return super(ChillerMaintenance, self).__unicode__() + ' (%s %s)' % (self.flow, self.type)


class Chiller(Component):
	flow = models.ForeignKey(base.Flow)
	type = models.ForeignKey(SystemType)

	repairs = ChillerRepair
	maintenances = ChillerMaintenance

	a = cached_property(lambda self: {'Scroll': 6629.4, 'Screw': 4997.2}[self.type.name], '_a')
	b = cached_property(lambda self: {'Scroll': -0.511, 'Screw': -0.431}[self.type.name], '_b')

	@cached_property
	def repair_cost(self):
		return self.bestfit(self.repairs.objects.filter(type=self.type, flow=self.flow)).cost_per_ton

	@cached_property
	def maintenance_cost(self):
		return self.bestfit(self.maintenances.objects.filter(type=self.type, flow=self.flow)).cost

	def __unicode__(self):
		return '%.2f ton, %s %s %s system' % (self.tons, price(self.cost), self.flow, self.type)


class ChillerReplace(Replace):
	unit = models.ForeignKey(Chiller, related_name='replacements')

	class Meta(Replace.Meta):
		verbose_name_plural = 'chiller replacements'

##################
# Cooling Towers #
##################

class CoolingTowerRepair(Repair):
	pass


class CoolingTowerMaintenance(Maintenance):
	pass


class CoolingTower(Component):
	repairs = CoolingTowerRepair
	maintenances = CoolingTowerMaintenance
	(a, b) = (664.48, -0.178)


class CoolingTowerReplace(Replace):
	unit = models.ForeignKey(CoolingTower, related_name='replacements')

	class Meta(Replace.Meta):
		verbose_name_plural = 'cooling tower replacements'

#####################################
# Systems
#####################################

class CoolingSystem(models.Model):
	number = models.CharField(max_length=15)
	description = models.CharField(max_length=255)

	cost = fields.CostField()
	tons = uscs.TonField()
	square_feet = uscs.SquareFootField()

	fan_coil = models.ForeignKey(FanCoil, blank=True, null=True)
	chiller = models.ForeignKey(Chiller, blank=True, null=True)
	cooling_tower = models.ForeignKey(CoolingTower, blank=True, null=True)

	def __iter__(self):
		return iter(self.components)

	@cached_property
	def components(self):
		return tuple(filter(bool, (self.fan_coil, self.chiller, self.cooling_tower)))

	@cached_property
	def initial_fixed_cost(self):
		return self.cost - sum(c.average_cost(self.tons) for c in self.components)

	@cached_property
	def fixed_cost_per_square_foot(self):
		return self.initial_fixed_cost / self.square_feet

	def fixed_cost(self, building):
		return self.fixed_cost_per_square_foot * building.square_feet

	def cost_for(self, building, mbh, tons):
		tons = tons.into(cooling)
		cost_per_ton = sum(c.marginal_cost(tons) for c in self.components)
		return (cost_per_ton * tons) + self.fixed_cost(building)

	def original_cost(self, building):
		return self.cost_for(building, None, self.tons)

	def __unicode__(self):
		return u'%s ft\u00B2, %.2f ton, %s unit' % (intcomma(self.square_feet.just('ft**2')), self.tons, price(self.cost))


class Rates(models.Model):
	component = models.ForeignKey(ContentType, limit_choices_to={'pk__in': components})
	zone = models.ForeignKey(Zone)
	repair = fields.YearField()
	replace = fields.YearField()

	class Meta:
		verbose_name_plural = 'rate sets'
		ordering = 'component', 'zone'

	def __unicode__(self):
		return 'Rates for %s in zone %s' % (self.component, self.zone)
