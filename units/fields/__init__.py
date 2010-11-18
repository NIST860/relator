from decimal import Decimal
from relator.units import *
from relator.units.metric import *
from relator.units.uscs import *
from relator.units import forms
from quantities import markup, Quantity as BaseQuantity
from django.db import models
markup.config.use_unicode = True


def UnitField(unit, parent=None, title=None):
	title = title or repr(Quantity(1, unit))[11:]
	formfield = forms.UnitField(unit)

	class UnitField(parent or models.FloatField):
		__metaclass__ = models.SubfieldBase

		def __init__(self, *args, **kwargs):
			kwargs['help_text'] = ('%s (%s)' % (kwargs.get('help_text', ''), title)).strip()
			super(UnitField, self).__init__(*args, **kwargs)

		def to_python(self, value):
			if value is None or isinstance(value, Quantity):
				return value
			return Quantity(value, unit).view()

		def get_prep_value(self, value):
			if value is None: return None
			if isinstance(value, BaseQuantity):
				value = 1 * value
				try:
					value.units = unit
				except ValueError as e:
					raise ValueError('In %s: %s' % (self.name, e.args[0]))
				return value.item()
			elif isinstance(value, (int, long, float, Decimal)):
				return value
			raise ValueError('In %s: Unknown quantity type: %s' % (self.name, value))

		def formfield(self, **kwargs):
			kwargs.setdefault('form_class', formfield)
			return super(UnitField, self).formfield(**kwargs)

	return UnitField


CostField = UnitField('dollar')
YearField = UnitField('years', models.PositiveSmallIntegerField)



class HourOfTheYear(int):
	hour = property(lambda self: self % 24)
	day = property(lambda self: self // 24)


class HourOfTheYearField(models.PositiveIntegerField):
	__metaclass__ = models.SubfieldBase

	def to_python(self, value):
		value = super(HourOfTheYearField, self).to_python(value)
		return None if value is None else HourOfTheYear(value)
