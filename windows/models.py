import re
from quantities import ft

from django.db import models
from django.db.models import F
from django.core.exceptions import ValidationError

from relator.constants.models import ConstantMRRModel
from relator.components.models import Component

from relator.units import dollar
from relator.units.fields import uscs

from relator.utilities.models import Type
from relator.utilities.decorators import cached_property


class Direction(Type):
	pass 


class Operability(Type):
	class Meta:
		verbose_name_plural ='operability types'


class Film(Type):
	cost = uscs.CostPerSquareFootField()


class Frame(Type):
	order = models.PositiveSmallIntegerField(default=0)
	cost = uscs.CostPerSquareFootField()

	class Meta:
		ordering = 'order',



class ASHRAEWindow(models.Model):
	identifier = models.CharField(max_length=100)
	operability = models.ForeignKey(Operability)

	u_factor = uscs.UValueField(verbose_name='U-Factor (US)', help_text='(BTU / h*ft^2*F)')
	shgc = models.FloatField(verbose_name='SHGC', help_text='(ratio, 0 to 1)')
	vt = models.FloatField(verbose_name='VT', help_text='(ratio, 0 to 1)')

	panes = models.PositiveSmallIntegerField(default=1)
	e_coatings = models.PositiveSmallIntegerField(help_text='(number of coatings)')
	frame = models.ForeignKey(Frame)
	film = models.ForeignKey(Film, verbose_name='Color/Film', blank=True, null=True)

	class Meta:
		verbose_name = 'ASHRAE Window'
		ordering = '-u_factor', '-shgc', '-vt'

	def __unicode__(self):
		return ', '.join(map(str, (self.operability, self.frame, 'panes: %s' % self.panes, self.film)))


class RSMeansWindow(ConstantMRRModel):
	number = models.CharField(max_length=15, unique=True)
	description = models.CharField(max_length=255)
	operability = models.ForeignKey(Operability)
	panes = models.PositiveSmallIntegerField(default=1)
	frame = models.ForeignKey(Frame, blank=True, null=True)
	film = models.ForeignKey(Film, verbose_name='Color/Film', blank=True, null=True)
	material_cost = uscs.CostPerSquareFootField()
	labor_cost = uscs.CostPerSquareFootField()

	class Meta:
		verbose_name = 'RS-Means Window'
		ordering = 'operability', 'frame', 'panes'

	def insulated(self):
		if self.panes == 2:
			return self
		for improvement in (
				self.description.replace('standard glass', 'insulated glass'),
				self.description.replace('standard glass', 'insulating glass'),
				self.description.replace('standard glazing', 'insulated glass'),
				self.description.replace('standard glazing', 'insulating glass')):
			try:
				return self.__class__.objects.get(description=improvement)
			except self.__class__.DoesNotExist:
				continue
		raise

	@property
	def cost(self):
		return self.material_cost + self.labor_cost

	def __unicode__(self):
		match = re.search(r'(\d+\'(?:-\d")? x \d+\'(?:-\d")?)', self.description)
		size = match.groups()[0] if match else ''
		words = self.description.split(', ')
		rel = words[2]
		if not size: size = words[-1]
		return ', '.join(map(str, (self.frame, rel, '%d pane' % self.panes, size)))


class WindowModifier(models.Model):
	name = models.SlugField(primary_key=True)
	rate = models.FloatField()

	def __unicode__(self):
		return '%s: %0.2f' % (self.name, self.rate)


class WindowComponent:
	rates = lambda self, zone: RSMeansWindow.rates(zone)
	maintenance_cost = 0 * dollar
	repair_cost = property(lambda self: 0.01 * self.cost)
	replacement_cost = 0 * dollar

	def __init__(self, old, stats):
		self.old, self.stats = old, stats
		self.size = stats.area.into(ft**2)

	__unicode__ = lambda self: unicode(self.cost)
	__str__ = lambda self: str(self.cost)

	@cached_property
	def new(self):
		u = self.stats.u_value.into('BTU / (h * ft**2 * degF)')
		filter = {'u_factor__lte': u, 'shgc__lte': self.stats.shgc, 'vt__lte': self.stats.vt}
		windows = ASHRAEWindow.objects.filter(operability=self.old.operability)
		options = windows.filter(**filter)
		frames = ('Aluminum', 'Aluminum with Break')
		sets = (options.filter(frame__name__in=frames), options.exclude(frame__name__in=frames))
		for set in sets:
			if not set.count(): continue
			return set.order_by('frame__cost', 'film__cost', 'e_coatings')[0]
		return windows.order_by('u_factor', 'shgc', 'vt')[0]

	@cached_property
	def cost(self):
		none = 0 * (dollar / ft**2)
		base = self.old.insulated()
		cost = base.material_cost * 1
		cost -= (self.old.frame.cost if self.old.frame else none)
		cost -= (self.old.film.cost if self.old.film else none)
		cost *= 1 + (self.new.e_coatings * WindowModifier.objects.get(name='e-coatings').rate)
		cost += (self.new.frame.cost if self.new.frame else none)
		cost += (self.new.film.cost if self.new.film else none)
		return cost + base.labor_cost
