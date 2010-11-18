from django.db import models
from relator.units import fields
from relator.units.fields import metric


class FuelData(models.Model):
	eplus = models.ForeignKey('data.EnergyPlusData', related_name='fuel_data')
	fuel = models.ForeignKey('assemblies.Fuel')
	hour = fields.HourOfTheYearField()
	use = metric.GigaJouleField()

	class Meta:
		unique_together = 'eplus', 'fuel', 'hour'

	def __unicode__(self):
		return '%s fuel data for %s at hour %d' % (self.fuel, self.eplus, self.hour)
