from django import forms
from django.contrib.contenttypes.models import ContentType
from relator.standards.models import Overhang


class StandardAppliedZoneForm(forms.ModelForm):
	zone = forms.ModelChoiceField(queryset=ContentType.objects.none())

	def __init__(self, *args, **kwargs):
		super(StandardAppliedZoneForm, self).__init__(*args, **kwargs)
		instance = kwargs.get('instance')
		data = args[0] if len(args) else kwargs.get('data', kwargs.get('initial'))
		if instance:
			Zone = instance.standard.zone_type.model_class()
			self.fields['zone'].queryset = Zone.objects.all()
			self.fields['zone'].initial = instance.zone_pk
			self.fields['zone'].label = unicode(Zone._meta.verbose_name)
		elif data:
			try:
				standard = self.fields['standard'].clean(data.get('standard'))
			except forms.ValidationError:
				pass
			else:
				self.fields['zone'].queryset = standard.zone_type.model_class().objects.all()

	def clean(self, *args, **kwargs):
		data = super(StandardAppliedZoneForm, self).clean(*args, **kwargs)
		standard = data.get('standard')
		zone = data.get('zone')
		if zone and standard:
			if ContentType.objects.get_for_model(zone) != standard.zone_type:
				raise forms.ValidationError('Please select a zone of type %s' % standard.zone_type)
		return data

	def save(self, *args, **kwargs):
		if self.cleaned_data.get('zone') is not None:
			self.instance.zone_pk = self.cleaned_data['zone'].pk
		return super(StandardAppliedZoneForm, self).save(*args, **kwargs)


def current_element_form(ModelClass, type):
	class ElementValueForm(StandardAppliedZoneForm):
		class Meta:
			model = ModelClass
			fields = type, 'standard', 'zone', 'r'
	return ElementValueForm
