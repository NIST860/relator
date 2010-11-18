from django.db import models

from relator.insulation.models import BlanketWallInsulation, RigidWallInsulation, RigidRoofInsulation
from relator.windows.models import RSMeansWindow as Window
from relator.heating.models import HeatingSystem, EnergySupply
from relator.cooling.models import CoolingSystem
from relator.packaged.models import PackagedUnit

from relator.units import fields
from relator.units.fields import uscs

from relator.utilities.models import Type
from relator.utilities.templatetags.utils import price
from relator.utilities.decorators import cached_property


class Roof(Type): pass
class Wall(Type): pass


class Building(models.Model):
	type = models.CharField(max_length=6, primary_key=True)
	name = models.CharField(max_length=50)
	life = fields.YearField(verbose_name='Service Life')
	roof = models.ForeignKey(Roof)
	wall = models.ForeignKey(Wall)

	stories = models.PositiveSmallIntegerField()
	story_height = uscs.FootField(help_text='(in feet)')
	width = uscs.FootField(help_text='East/West (in feet)')
	length = uscs.FootField(help_text='North/South (in feet)')

	blanket_wall_insulation = models.ForeignKey(BlanketWallInsulation, blank=True, null=True)
	rigid_wall_insulation = models.ForeignKey(RigidWallInsulation, blank=True, null=True)
	roof_insulation = models.ForeignKey(RigidRoofInsulation, blank=True, null=True)

	window = models.ForeignKey(Window)

	energy_supply = models.ForeignKey(EnergySupply, blank=True, null=True)
	heating_system = models.ForeignKey(HeatingSystem, blank=True, null=True)
	cooling_system = models.ForeignKey(CoolingSystem, blank=True, null=True)
	packaged_unit = models.ForeignKey(PackagedUnit, blank=True, null=True)

	fixtures = models.FloatField(help_text='(in fixtures per 1000 square feet)')
	subtotal = fields.CostField()
	release_year = fields.YearField()

	class Meta:
		ordering = 'type',

	@cached_property
	def perimiter(self):
		return (2 * self.width) + (2 * self.height)

	@cached_property
	def height(self):
		return self.story_height * self.stories

	@cached_property
	def square_feet(self):
		return self.footprint * self.stories

	@cached_property
	def footprint(self):
		return self.width * self.height

	def __unicode__(self):
		return self.name.title()


class Cost(models.Model):
	building = models.ForeignKey(Building, related_name='costs')
	year = models.PositiveSmallIntegerField()
	total_cost = uscs.CostPerSquareFootField(verbose_name=u'$ per ft\xB2')
	hvac_cost = uscs.CostPerSquareFootField(verbose_name='HVAC Cost')

	class Meta:
		ordering = 'building', 'year',
		unique_together = 'building', 'year',

	@cached_property
	def cost(self):
		return self.total_cost - self.hvac_cost

	def __unicode__(self):
		cost = price(self.total_cost)
		return '%s after %s year: %s' % (self.building, self.year, cost)
