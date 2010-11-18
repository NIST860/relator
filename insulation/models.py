from quantities import ft, markup
markup.config.use_unicode = False

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.encoding import smart_unicode as u

from relator.components.models import Component

from relator.units import dollar
from relator.units.fields import uscs

from relator.utilities.models import Type


class InsulationType(Type):
	strip = models.BooleanField(default=False)


class Insulation(Component):
	type = models.ForeignKey(InsulationType)
	r = models.FloatField(verbose_name='R-Value (US)', help_text='(US Common System: h*ft^2*F / BTU)', blank=True, null=True)
	thickness = uscs.InchField()

	class Meta:
		abstract = True
		ordering = 'type', 'r'

	def __unicode__(self):
		if self.r is None:
			return 'Insulation not possible'
		return u'{0}, {1}: R{2}, {3}'.format(*map(u, (self.type, self.thickness, self.r, self.cost)))

	@classmethod
	def oftype(cls, obj):
		type = cls.default() if obj is None else obj.type
		if type.strip:
			type = cls.default()
		return cls.objects.filter(type=type).order_by('r')

	@classmethod
	def next(cls, options, r):
		try:
			return options.order_by('-r').filter(r__lte=r)[0]
		except IndexError:
			return options.order_by('r')[0]

	@classmethod
	def sheets(cls, location, building, standard, r=None):
		if r is None:
			zone = location.climate_zone(standard)
			r = cls.r(standard, building, zone)
		options = cls.oftype(cls.on(building))
		while r > 0:
			next = cls.next(options, r)
			if next.r is None: return
			elif next.r: yield next
			r -= next.r


class BlanketWallInsulation(Insulation):
	default = classmethod(lambda cls: InsulationType.objects.get(name='Unfaced fiberglass'))
	width = models.FloatField(help_text='(in inches)', blank=True, null=True)
	on = classmethod(lambda cls, building: building.blanket_wall_insulation)
	r = classmethod(lambda cls, standard, building, zone: standard.wall_r(building.wall, zone))

	@classmethod
	def sheets(cls, *args, **kwargs):
		for next in super(BlanketWallInsulation, cls).sheets(*args, **kwargs):
			yield next
			break


class RigidWallInsulation(Insulation):
	default = classmethod(lambda cls: InsulationType.objects.get(name='Extruded polystyrene'))
	on = classmethod(lambda cls, building: building.rigid_wall_insulation)
	r = classmethod(lambda cls, standard, building, zone: standard.wall_r(building.wall, zone))


class RigidRoofInsulation(Insulation):
	default = classmethod(lambda cls: InsulationType.objects.get(name='Extruded polystyrene 15 PSI'))
	on = classmethod(lambda cls, building: building.roof_insulation)
	r = classmethod(lambda cls, standard, building, zone: standard.roof_r(building.roof, zone))
