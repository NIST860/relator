import re
from quantities import markup
from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from django.utils import formats
from relator.units import *
from relator.units.metric import *
from relator.units.uscs import *
markup.config.use_unicode = True


def UnitField(unit):
	display = re.sub(r'\bkft3\b', 'kft**3', unit)
	display = re.sub(r'\bdollars?\b', r'$', display)
	display = re.sub(r'\*\*(\d+)', r'^\1', display)

	class UnitWidget(forms.MultiWidget):
		def __init__(self, attrs=None):
			widgets = [forms.TextInput(attrs=attrs), forms.TextInput(attrs=attrs)]
			super(UnitWidget, self).__init__(widgets, attrs)

		def decompress(self, value):
			if value:
				return [value.just(unit), display]
			return [None, None]

	class UnitField(forms.MultiValueField):
		widget = UnitWidget

		def __init__(self, attrs=None, *args, **kwargs):
			fields = (forms.FloatField(*args, **kwargs), forms.CharField(required=False))
			super(UnitField, self).__init__(fields, attrs)

		def clean(self, value):
			if value is None: return None
			return super(UnitField, self).clean(value)

		def compress(self, data_list):
			if not data_list: return None
			value, units = data_list
			units = (units or unit)
			units = re.sub(r'\^(\d+)', r'**\1', units)
			units = re.sub(r'\$', r'dollar', units)
			units = re.sub(r'kft\*\*3', r'kft3', units)
			return Quantity(value, units or unit)

	return UnitField
