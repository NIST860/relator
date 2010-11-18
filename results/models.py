from django.db import models
from relator.units import fields, Quantity
from relator.units.fields import metric, uscs

class ResultSet(models.Model):
	deflator = models.DecimalField(max_digits=8, decimal_places=6)
	marr = models.DecimalField(max_digits=8, decimal_places=6)

	class Meta:
		unique_together = 'deflator', 'marr'

	def __unicode__(self):
		return 'Results with %s deflator and %s marr' % (self.deflator, self.marr or self.deflator)


class Row(models.Model):
	set = models.ForeignKey(ResultSet)
	building = models.ForeignKey('structures.Building')
	location = models.ForeignKey('locations.Location')
	standard = models.ForeignKey('standards.Standard')
	eps = models.FloatField()

	class Meta:
		unique_together = 'set', 'building', 'location', 'standard'

	def __unicode__(self):
		return '%s, %s, %s' % (self.building, self.location, self.standard)


class Costs(models.Model):
	row = models.ForeignKey(Row, related_name='costs')
	period = fields.YearField()
	lifecycle_cost = fields.CostField()
	efficiency_cost = fields.CostField()
	energy_cost = fields.CostField()
	energy_use = metric.KiloWattHourField()
	gas_use = uscs.BTUperYearField()
	electricity_use = uscs.BTUperYearField()

	class Meta:
		unique_together = 'row', 'period'

	def __unicode__(self):
		return 'Deltas for %s' % self.row


class Emission(models.Model):
	row = models.ForeignKey(Row, related_name='emissions')
	emission = models.ForeignKey('carbon.EmissionType')
	amount = models.FloatField()
	total = property(lambda self: Quantity(self.amount, self.emission.unit))

	class Meta:
		unique_together = 'row', 'emission'

	def __unicode__(self):
		return '%s for %s' % (self.emission, self.row)


class Impact(models.Model):
	row = models.ForeignKey(Row, related_name='impacts')
	impact = models.ForeignKey('carbon.Impact')
	amount = models.FloatField()
	total = property(lambda self: Quantity(self.amount, self.impact.unit))

	class Meta:
		unique_together = 'row', 'impact'

	def __unicode__(self):
		return '%s for %s' % (self.impact, self.row)


class Base(models.Model):
	set = models.ForeignKey(ResultSet)
	building = models.ForeignKey('structures.Building')
	location = models.ForeignKey('locations.Location')
	period = fields.YearField()
	residual = fields.CostField()

	class Meta:
		unique_together = 'building', 'location', 'period'

	def __unicode__(self):
		return 'Base for %s, %s, %s' % (self.building, self.location, self.period)


class CarbonFunction(models.Model):
	name = models.SlugField(primary_key=True, choices=(
		('low', 'Low'),
		('medium', 'Meidum'),
		('high', 'High')))
	building = models.ForeignKey('structures.Building')
	location = models.ForeignKey('locations.Location')
	standard = models.ForeignKey('standards.Standard')
	year = fields.YearField()
	emissions = metric.GramField()
	price = metric.CostPerGramField()

	@property
	def cost(self):
		return self.emissions * self.price
