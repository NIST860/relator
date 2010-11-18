from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from relator.utilities.decorators import cache
from relator.structures.models import Wall, Roof
from relator.lighting.models import Overhang
from relator.zones.models import Ashrae04
from relator.units import fields


def zones():
	return ContentType.objects.filter(app_label='zones').values_list('pk', flat=True)


class Standard(models.Model):
	name = models.CharField(max_length=50, unique=True)
	year = models.PositiveSmallIntegerField(unique=True)
	zone_type = models.ForeignKey(ContentType, limit_choices_to={'pk__in': zones})
	use_daylighting = models.BooleanField(default=False)
	
	class Meta:
		ordering = 'name',

	def __unicode__(self):
		return self.name

	def wall_r(self, wall, zone):
		assert isinstance(zone, self.zone_type.model_class())
		return self.wallvalues.get(zone_pk=zone.pk, wall=wall).r

	def roof_r(self, roof, zone):
		assert isinstance(zone, self.zone_type.model_class())
		return self.roofvalues.get(zone_pk=zone.pk, roof=roof).r

	@cache
	def overhang(self, zone):
		assert isinstance(zone, self.zone_type.model_class())
		try:
			return self.overhangdatas.get(zones=zone).overhang
		except self.overhangdatas.model.DoesNotExist:
			return None

	def use_overhang(self, zone):
		return self.overhang(zone) is not None

##########################################
# Components
##########################################

class StandardAppliedValue(models.Model):
	standard = models.ForeignKey(Standard, related_name='%(class)ss')
	zone_pk = models.PositiveIntegerField()

	class Meta:
		abstract = True

	def _get_zone(self):
		return self.standard.zone_type.get_object_for_this_type(pk=self.zone_pk)
	def _set_zone(self, zone):
		if ContentType.objects.get_for_model(zone) != self.standard.zone_type:
			raise ValueError('Object %s is not of zone %s' % (zone, self.stardard.zone_type))
		self.zone_pk = zone.pk
	zone = property(_get_zone, _set_zone)

##########################################
# Lighting Data
##########################################

class OverhangData(models.Model):
	standard = models.ForeignKey(Standard, related_name='overhangdatas')
	overhang = models.ForeignKey(Overhang)
	zones = models.ManyToManyField(Ashrae04)
	
	def __unicode__(self):
		zones = ','.join(map(str, self.zones.all()))
		return '%s uses %s in zones %s' % (self.standard, self.overhang, zones)

##########################################
# Structure Data
##########################################

class StructureValue(StandardAppliedValue):
	r = models.FloatField(verbose_name='R-Value (US)', help_text='(US Common System: h*ft^2*F / BTU)')

	class Meta:
		abstract = True

	def __unicode__(self):
		return '%s / %s - %s: %s' % (self.standard, self.zone, self.element, self.r)

class WallValue(StructureValue):
	wall = models.ForeignKey(Wall)
	element = property(lambda s: s.wall)

class RoofValue(StructureValue):
	roof = models.ForeignKey(Roof)
	element = property(lambda s: s.roof)
