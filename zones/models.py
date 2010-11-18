from django.contrib.contenttypes.models import ContentType
from django.db import models


class Ashrae04(models.Model):
	number = models.PositiveSmallIntegerField()
	subzone = models.CharField(max_length=1, blank=True, default='')

	class Meta:
		ordering = 'number', 'subzone'
		unique_together = 'number', 'subzone'
		verbose_name = 'ASHRAE 2004 Climate Zone'

	def __unicode__(self):
		return '%d%s' % (self.number, self.subzone)


class Ashrae01(models.Model):
	number = models.PositiveSmallIntegerField(unique=True)

	class Meta:
		ordering = 'number',
		verbose_name = 'ASHRAE 2001 Climate Zone'

	def __unicode__(self):
		return unicode(self.number)


class HVAC(models.Model):
	number = models.PositiveSmallIntegerField(unique=True)

	class Meta:
		ordering = 'number',
		verbose_name = 'Whitestone HVAC Zone'

	def __unicode__(self):
		return unicode(self.number)


class CensusRegion(models.Model):
	number = models.PositiveSmallIntegerField(unique=True)
	name = models.CharField(max_length=50)

	class Meta:
		ordering = 'name',

	def __unicode__(self):
		return self.name.title()


class CensusZone(models.Model):
	parent = models.ForeignKey(CensusRegion, related_name='zones')
	name = models.CharField(max_length=50)

	class Meta:
		ordering = 'name',

	def __unicode__(self):
		return self.name.title()
