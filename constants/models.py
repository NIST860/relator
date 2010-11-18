from django.db import models
from django.contrib.contenttypes.models import ContentType

from relator.assemblies.models import Fuel
from relator.locations.models import State
from relator.zones.models import CensusRegion

from relator.units import fields
from relator.units.fields import metric

from relator.utilities import inherits


class PriceIndex(models.Model):
	fuel = models.ForeignKey(Fuel)
	year = fields.YearField()
	zone = models.ForeignKey(CensusRegion)
	value = models.FloatField()

	class Meta:
		unique_together = 'fuel', 'year', 'zone'
		ordering = 'fuel', 'year', 'zone'
		verbose_name_plural = 'price indicies'

	@classmethod
	def upv(cls, fuel, zone, year, rate):
		indicies = cls.objects.filter(fuel=fuel, zone=zone, year__lte=year).order_by('year')
		discount = lambda i: i.value / ((1 + rate) ** i.year.just('year'))
		return sum(map(discount, indicies))

	def __unicode__(self):
		return '%s price index for year %s in zone %s' % (self.fuel, self.year, self.zone)


class Tariff(models.Model):
	fuel = models.ForeignKey(Fuel)
	state = models.ForeignKey(State)
	tariff = metric.CostPerKiloWattHourField()

	class Meta:
		unique_together = 'fuel', 'state'

	def __unicode__(self):
		return '%s %s tariff' % (self.state, self.fuel)


def components():
	iscomp = lambda c: inherits(c.model_class(), ConstantMRRModel)
	return (c.pk for c in filter(iscomp, ContentType.objects.all()))


class MRRRates(models.Model):
	component = models.ForeignKey(ContentType, primary_key=True, limit_choices_to={'pk__in': components})
	repair = fields.YearField()
	replace = fields.YearField()

	class Meta:
		verbose_name = 'maintenance/repair/replace rates'
		verbose_name_plural = 'maintenance/repair/replace rate sets'

	def __unicode__(self):
		return unicode(self.component).title()


class ConstantMRRModel(models.Model):
	class Meta:
		abstract = True

	@classmethod
	def rates(cls, zone=None):
		type = ContentType.objects.get_for_model(cls)
		return MRRRates.objects.get(component=type)
