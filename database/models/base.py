from django.db import models
from quantities import Quantity
from relator.units import fields
from relator.utilities.decorators import cached_property

class Cost(object):
	cost = property(lambda self: self.new)
	delta = property(lambda self: self.new - self.old)


class Results(models.Model):
	class Meta:
		abstract = True

	@classmethod
	def get(cls, *args, **kwargs):
		kwargs.update(zip((f.name for f in cls._meta.fields), args))
		try:
			return cls.objects.get(**kwargs)
		except cls.DoesNotExist:
			return cls.create(**kwargs)

	@classmethod
	def create(cls, *args, **kwargs):
		self = cls(**kwargs)
		self.make(*args, **kwargs)
		return self

	def make(self, *args, **kwargs):
		self.save()


class Database(Results):
	deflator = models.DecimalField(max_digits=8, decimal_places=6, primary_key=True)

	def spv(self, year):
		if isinstance(year, Quantity):
			year.units = 'year'
			year = int(year.item())
		return 1 / ((1 + float(self.deflator)) ** year)

	def __unicode__(self):
		return 'Results for %s%% interest' % (self.deflator * 100)


class Group(Results):
	database = models.ForeignKey(Database, related_name='groups')
	building = models.ForeignKey('structures.Building')
	location = models.ForeignKey('locations.Location')
	standard = models.ForeignKey('standards.Standard')

	class Meta:
		unique_together = 'database', 'building', 'location', 'standard'

	def __unicode__(self):
		return '%s, %s, %s' % (self.building, self.location, self.standard)

	def row_for(self, period):
		try:
			return self.rows.get(period=period)
		except self.rows.model.DoesNotExist:
			return self.rows.model.get(group=self, period=period)

	def index(self, cost, type):
		if not type: return cost
		return cost * self.location.indicies.get(index__pk=type).value

	def pv(self, cost, year):
		return cost * self.database.spv(year)

	@cached_property
	def simulation(self):
		from relator.data.models import EnergyPlusData
		return EnergyPlusData.objects.get(
				building=self.building,
				location=self.location,
				standard=self.standard)

	@cached_property
	def base(self):
		if self.standard.year == 1999:
			return self
		from standards.models import Standard
		base = Standard.objects.get(year=1999)
		return self.__class__.get(
				database=self.database,
				building=self.building,
				location=self.location,
				standard=base)

	@cached_property
	def options(self):
		from standards.models import Standard
		for standard in Standard.objects.all():
			yield self.__class__.get(
					database=self.database,
					building=self.building,
					location=self.location,
					standard=standard)


class Row(Results):
	group = models.ForeignKey(Group, related_name='rows')
	period = fields.YearField()

	year = property(lambda self: int(self.period.just('years')))
	years = property(lambda self: xrange(1, self.year + 1))

	def __unicode__(self):
		return u"%s: %s" % (self.group, self.period)

	def pv(self, cost, year=None):
		return self.group.pv(cost, year or self.year)

	@cached_property
	def base(self):
		return self.group.base.row_for(self.period)

	@cached_property
	def options(self):
		for group in self.group.options:
			yield group.row_for(self.period)
