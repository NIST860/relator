from django.db import models
from relator.zones.models import Ashrae04, Ashrae01, HVAC, CensusZone

class State(models.Model):
	"""
	This model simply represents a state. Providences / military
	establishments not found in a state may also be included.
	This will likely be static and probably will not change.
	The primary key is 'code', which is the two digit postal code
	of the state or providence.
	"""
	code = models.CharField(max_length=2, primary_key=True)
	name = models.CharField(max_length=50)
	census_zone = models.ForeignKey(CensusZone, blank=True, null=True, related_name='states')
	standard = models.ForeignKey('standards.Standard', blank=True, null=True)
	census_region = property(lambda self: self.census_zone.parent)

	class Meta:
		ordering = 'name',

	def __unicode__(self):
		return "{0} ({1})".format(self.name, self.code)


class County(models.Model):
	"""
	This is a county in a state. It is not required, and exists
	mainly to link many cities together in one area so that zones
	can be changed in groups instead of one at a time. For example,
	you can select all locations in a certain county and then change
	all of their zones at once. Keep in mind that not all locations
	will have a county.
	"""
	name = models.CharField(max_length=50)
	state = models.ForeignKey(State, related_name='counties')
	_standard = models.ForeignKey('standards.Standard', blank=True, null=True)

	class Meta:
		verbose_name_plural = 'counties'
		ordering = 'name', 'state'

	@property
	def standard(self):
		return self._standard or self.state.standard

	def __unicode__(self):
		return "{0} ({1})".format(self.name, self.state.code)


class Location(models.Model):
	"""
	This is a location, usually a city, sometimes a miliary base or other point of interest.
	It exists in a State (which may also be a providence), and may (or may not) provide a
	County for easy grouping. It also holds Zone data.
	"""
	name = models.CharField(max_length=50)
	state = models.ForeignKey(State, related_name='locations')
	county = models.ForeignKey(County, blank=True, null=True, related_name='locations')
	ashrae04 = models.ForeignKey(Ashrae04, verbose_name=Ashrae04._meta.verbose_name)
	ashrae04sub = models.CharField(max_length=1, blank=True, verbose_name='ASHRAE 2004 climate zubzone')
	ashrae01 = models.ForeignKey(Ashrae01, verbose_name=Ashrae01._meta.verbose_name)
	hvac = models.ForeignKey(HVAC, blank=True, null=True, verbose_name=HVAC._meta.verbose_name)
	_standard = models.ForeignKey('standards.Standard', blank=True, null=True)
	representative = models.BooleanField(default=False)

	class Meta:
		ordering = 'name', 'state'
		unique_together = 'name', 'state'

	@property
	def standard(self):
		next = self.county if self.county else self.state
		return self._standard or next.standard

	def climate_zone(self, standard):
		type = standard.zone_type.model_class()
		if type == Ashrae01:
			return self.ashrae01
		elif type == Ashrae04:
			return self.ashrae04
		raise ValueError('Can not determine climate zone for standard %s' % standard)

	def clean(self, *args, **kwargs):
		from django.core.exceptions import ValidationError
		if self.county and self.county.state != self.state:
			raise ValidationError("Locations can't be in a county that isn't in the same state.")
		return super(Location, self).clean(*args, **kwargs)

	def __unicode__(self):
		return "{0} ({1})".format(self.name, self.state.code)


class Index(models.Model):
	slug = models.SlugField(primary_key=True)
	name = models.CharField(max_length=32)
	description = models.CharField(max_length=100)
	locations = models.ManyToManyField(Location, through='LocationIndexValue')

	class Meta:
		ordering = 'name',
		verbose_name_plural = 'indicies'

	def __unicode__(self):
		return self.name


class LocationIndexValue(models.Model):
	index = models.ForeignKey(Index)
	location = models.ForeignKey(Location, related_name='indicies')
	value = models.FloatField()

	class Meta:
		ordering = 'index', 'location'
		unique_together = 'index', 'location'
		verbose_name = 'location index'
		verbose_name_plural = 'location indicies'

	def __unicode__(self):
		return '%s: %s' % (self.index, self.location)
