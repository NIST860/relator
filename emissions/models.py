from django.db import models
from django.db.models import Q
from relator.utilities.models import Type
from relator.units import Quantity, sum
from relator.units.fields import both

class EmissionType(Type):
	impacts = models.ManyToManyField('Impact',
			blank=True,
			null=True,
			through='Equivalence',
			related_name='types')
	unit = models.CharField(max_length=50, default='g')

	def total(self, state, usage):
		emissions = self.emissions.filter(Q(state=state) | Q(state=None))
		return sum(e.total(usage) for e in emissions)

	def __unicode__(self):
		return '%s (%s)' % (self.name, self.unit)


class Emission(models.Model):
	type = models.ForeignKey('EmissionType', related_name='emissions')
	fuel = models.ForeignKey('assemblies.Fuel')
	state  = models.ForeignKey('locations.State', blank=True, null=True)
	value = models.FloatField()

	class Meta:
		ordering = 'type', 'fuel', 'state'
		unique_together = 'type', 'fuel', 'state'

	@property
	def flow(self):
		return Quantity(self.value, '(%s) / BTU' % self.type.unit).view()

	def total(self, usage):
		none = Quantity(0, 'BTU')
		return self.flow * (usage.get(self.fuel, none).into('BTU') / year)

	def __unicode__(self):
		if self.state:
			return '%s: %s - %s' % (self.type, self.fuel, self.state)
		return '%s: %s' % (self.type, self.fuel)


class Equivalence(models.Model):
	emission = models.ForeignKey('EmissionType', related_name='equivalences')
	impact = models.ForeignKey('Impact', related_name='equivalences')
	equivalence = models.FloatField()

	class Meta:
		unique_together = 'emission', 'impact'

	def __unicode__(self):
		return '%s, %s - (%s)' % (self.emission, self.impact, self.equivalence)
	

class Impact(Type):
	normalization = models.FloatField()
	weight = models.DecimalField(max_digits=5, decimal_places=5)
	unit = models.CharField(max_length=50, default='g')
	n = property(lambda self: Quantity(self.normalization, self.unit))

	def total(self, state, usage):
		def totals():
			for equivalence in self.equivalences.select_related('type'):
				type, eq = equivalence.emission, equivalence.equivalence
				yield type.total(state, usage) * eq
		return sum(totals(), Quantity(0, self.unit))

	def normalize(self, value):
		return (value / self.n).simplified.item()

	def __unicode__(self):
		return '%s (%s)' % (self.name, self.unit)
