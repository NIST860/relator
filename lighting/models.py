from django.db import models
from relator.components.models import Component

class Overhang(Component):
	description = models.CharField(max_length=255)

	def __unicode__(self):
		return self.description


class DaylightSystem(Component):
	number = models.CharField(max_length=12)
	description = models.CharField(max_length=255)
	fixtures = models.FloatField(help_text='(in fixtures per 1000 square feet)')

	class Meta:
		ordering = 'fixtures',

	def __unicode__(self):
		return self.description
