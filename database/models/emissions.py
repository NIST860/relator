from django.db import models
from quantities import year
from base import Results
from fields import DataLinkField
from relator.units import fields, Quantity
from relator.utilities.decorators import cached_property
from carbon import models as data

class EmissionData(Results):
	group = DataLinkField('Group', 'emission')
	eps = models.FloatField(null=True)

	def make(self, group):
		self.save()
		impacts = data.Impact.objects.all()
		impacts = [Impact.create(data=self, impact=i) for i in impacts]
		types = data.EmissionType.objects.all()
		types = [Emission.create(data=self, type=t) for t in types]

		self.eps = sum(
			float(i.impact.weight) *
			i.impact.normalize(i.amount)
			for i in impacts)
		self.save()


class EmissionUnit(Results):
	data = models.ForeignKey(EmissionData)
	value = models.FloatField()

	class Meta:
		abstract = True

	@classmethod
	def base(cls, data, field, object):
		self = cls(data=data, **{field: object})
		state = data.group.location.state
		usage = data.group.row_for(1 * year).energy.usage
		self.value = object.total(state, usage)
		self.save()
		return self



class Impact(EmissionUnit):
	impact = models.ForeignKey(data.Impact, related_name='computed')
	amount = property(lambda self: Quantity(self.value, self.impact.unit))
	create = classmethod(lambda cls, data, impact: cls.base(data, 'impact', impact))


class Emission(EmissionUnit):
	type = models.ForeignKey(data.EmissionType, related_name='computed')
	amount = property(lambda self: Quantity(self.value, self.type.unit))
	create = classmethod(lambda cls, data, type: cls.base(data, 'type', type))
