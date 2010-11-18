from quantities import year
from django.db.models import Count
from relator.carbon.models import EmissionType, Impact
from relator.utilities.decorators import cached_property, cache
from relator.utilities.collections import OrderedDict
from base import Cost

class Emissions(Cost):
	def __init__(self, parent, carbon):
		self.carbon = carbon
		super(Emissions, self).__init__(parent)

	def total(self, flow, fuelcost):
		return flow.total(self.location.state, self.energy.usage)

	@cached_property
	def eps(self):
		return sum(float(i.weight) * v for (i, v) in self.normalized.items())

	@cached_property
	def normalized(self):
		return OrderedDict((i, i.normalize(v)) for (i, v) in self.impacts.items())

	@cached_property
	def impacts(self):
		def impact(i):
			return i, i.total(self.location.state, self.master.energy.usage)
		return OrderedDict(map(impact, Impact.objects.all()))

	@cached_property
	def emissions(self):
		def emission(e):
			return e, e.total(self.location.state, self.master.energy.usage)
		return OrderedDict(map(emission, EmissionType.objects.all()))

	@cache
	def cost(self, index=True):
		if self.carbon is None:
			return 0 * dollar

		Carbon = EmissionType.objects.get(pk=1)
		e1 = Carbon.total(self.location.state, self.master.energy.usage)

		if self.carbon in ('low', 'medium', 'high'):
			fn = CarbonFunction.objects.filter(name=self.carbon,
					building=self.building,
					location=self.location,
					standard=self.standard)
			return e1 * sum(fn.get(year=t).cost * self.spv(t) for t in self.master.years)
		else:
			carbon = Quantity(floaw(self.carbon), 'dollar / gram')
			return carbon * e1 * self.master.upv()

	@cache
	def delta(self, index=True):
		raise Exception('Change in carbon emissions unknown')
