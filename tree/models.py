from quantities import J, kWh
from django.db import models
from django.db.models import Sum
from relator.units import fields, dollar
from relator.units.fields import metric
from relator.utilities.decorators import cached_property

class Snapshot(models.Model):
	location = models.CharField(max_length=50)
	age = fields.YearField()
	x = models.PositiveSmallIntegerField()
	y = models.PositiveSmallIntegerField()

	class Meta:
		ordering = 'location', 'age', 'x', 'y'

	def __unicode__(self):
		return '%s old tree in %s at (%s, %s)' % (self.age, self.location, self.x, self.y)
	
	def use(self, fuel):
		return self.uses.filter(fuel=fuel).aggregate(use=Sum('use'))['use'] or (0 * J)


class Results(object):
	def __init__(self, tree):
		from assemblies.models import Fuel
		electric = Fuel.objects.get(name='Electric')
		gas = Fuel.objects.get(name='Gas')

		electric_use = tree.use.filter(fuel=electric).aggregate(Sum('use'))['use__sum'] or (0 * J)
		gas_use = tree.use.filter(fuel=gas).aggregate(Sum('use'))['use__sum'] or (0 * J)
		total_use = electric_use + gas_use

		peak_electric = tree.demand.get(fuel__name='Electric').max
		peak_gas = tree.demand.get(fuel__name='Gas').max

		electric_cost = self.electric_cost(electric_use)
		gas_cost = self.gas_cost(gas_use)
		total_cost = electric_cost + gas_cost

	def electric_cost(self, use):
		e = use.just('kWh')
		ea = min(700, e)
		eb = max(0, min(1000, e) - 700)
		ec = max(0, e - 1000)
		return ((ea * 0.092) + (eb * 0.157) + (ec * 0.176)) * dollar

	def gas_cost(self, use):
		g = use.just('therm')
		return (0.647292 * g) + max(0.09863 * 365, 0.44369 * g)


class PeakDemand(models.Model):
	tree = models.ForeignKey(Snapshot, related_name='demands')
	fuel = models.ForeignKey('assemblies.Fuel')
	max = metric.WattField()

	class Meta:
		unique_together = 'tree', 'fuel'

	def __unicode__(self):
		return 'Peak %s for %s: %s' % (self.fuel, self.tree, self.max)


class EnergyUse(models.Model):
	tree = models.ForeignKey(Snapshot, related_name='uses')
	fuel = models.ForeignKey('assemblies.Fuel')
	month = models.PositiveSmallIntegerField()
	use = metric.JouleField()

	class Meta:
		unique_together = 'tree', 'fuel', 'month'

	def __unicode__(self):
		return '%s use for %s in month %s: %s' % (self.fuel, self.tree, self.month, self.use)


class Results(object):
	def __init__(self, tree):
		from assemblies.models import Fuel
		electric = Fuel.objects.get(name='Electric')
		gas = Fuel.objects.get(name='Gas')

		electric_use = tree.use.filter(fuel=electric).aggregate(Sum('use'))['use__sum'] or (0 * J)
		gas_use = tree.use.filter(fuel=gas).aggregate(Sum('use'))['use__sum'] or (0 * J)
		total_use = electric_use + gas_use

		peak_electric = tree.demand.get(fuel__name='Electric').max
		peak_gas = tree.demand.get(fuel__name='Gas').max

		electric_cost = self.electric_cost(electric_use)
		gas_cost = self.gas_cost(gas_use)
		total_cost = electric_cost + gas_cost

	def electric_cost(self, use):
		e = use.just('kWh')
		ea = min(700, e)
		eb = max(0, min(1000, e) - 700)
		ec = max(0, e - 1000)
		return ((ea * 0.092) + (eb * 0.157) + (ec * 0.176)) * dollar

	def gas_cost(self, use):
		g = use.just('therm')
		return (0.647292 * g) + max(0.09863 * 365, 0.44369 * g)
