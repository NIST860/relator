from django.db import models

from relator.locations.models import Location
from relator.structures.models import Building
from relator.standards.models import Standard
from relator.insulation.models import Insulation
from relator.windows.models import RSMeansWindow as Window, Direction
from relator.assemblies.models import Fuel

from relator.units.fields import metric

from relator.utilities.models import Type


class EnergyPlusData(models.Model):
	location = models.ForeignKey(Location)
	building = models.ForeignKey(Building)
	standard = models.ForeignKey(Standard)

	heating_capacity = metric.WattField()
	cooling_capacity = metric.WattField()
	area = metric.SquareMeterField()
	overhang_area = metric.SquareMeterField()

	max_electricity = metric.WattField()

	window_ratio = property(lambda self: self.windowratios.get())
	wall_area = property(lambda self: self.window_ratio.gross - self.window_ratio.opening)
	skylight_ratio = property(lambda self: self.windowratios.get())
	roof_area = property(lambda self: self.skylight_ratio.gross - self.skylight_ratio.opening)

	class Meta:
		verbose_name_plural = 'Energy Plus data sets'
		unique_together = 'location', 'building', 'standard'
		ordering = 'location', 'building', 'standard'

	def __unicode__(self):
		return '%s - %s - %s' % (self.building, self.location, self.standard)


class Ratio(models.Model):
	eplus = models.ForeignKey(EnergyPlusData, related_name='%(class)ss', primary_key=True)
	gross = metric.SquareMeterField()
	opening = metric.SquareMeterField()

	class Meta:
		abstract = True

	def __unicode__(self):
		return '%s for %s' % (self._meta.verbose_name, self.eplus)

class WindowRatio(Ratio): pass
class SkylightRatio(Ratio): pass


class FuelEndUse(models.Model):
	eplus = models.ForeignKey(EnergyPlusData, related_name='fuel_enduses')
	fuel = models.ForeignKey(Fuel)
	heating = metric.GigaJouleField()
	cooling = metric.GigaJouleField()
	total = metric.GigaJouleField()

	class Meta:
		unique_together = 'eplus', 'fuel'

	def __unicode__(self):
		return '%s end use for %s' % (self.fuel, self.eplus)


class WindowData(models.Model):
	eplus = models.ForeignKey(EnergyPlusData, related_name='windows')
	direction = models.ForeignKey(Direction)
	area = metric.SquareMeterField()
	u_value = metric.UValueField(verbose_name='U-Value')
	shgc = models.FloatField(verbose_name='SHGC')
	vt = models.FloatField(verbose_name='VT')

	class Meta:
		verbose_name_plural = 'window data sets'
		unique_together = 'eplus', 'direction'

	def __unicode__(self):
		return '%s window data for %s' % (self.direction, self.eplus)
