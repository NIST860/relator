from django import forms
from decimal import Decimal, InvalidOperation

class VariableForm(forms.Form):
	deflator = forms.DecimalField()
	marr = forms.DecimalField(required=False, label='MARR')

	def clean(self, *args, **kwargs):
		data = super(VariableForm, self).clean(*args, **kwargs)
		carbon = self.data.get('carbon')
		if carbon == 'none':
			data['carbon'] = None
		elif carbon == 'constant':
			try:
				data['carbon'] = str(Decimal(self.data.get('carbon-constant').strip('$ ')))
			except InvalidOperation:
				raise forms.ValidationError('Unacceptable carbon constant: %s' % self.data.get('carbon-constant'))
		elif carbon == 'function':
			data['carbon'] = self.data.get('carbon-function')
			if data['carbon'] not in ('low', 'medium', 'high'):
				raise forms.ValidationError('Unacceptable carbon function: %s' % self.data.get('carbon-function'))
		else:
			raise forms.ValidationError('Unrecognized carbon mode: %s' % carbon)
		return data

	def variables(self):
		return dict(self.cleaned_data)
