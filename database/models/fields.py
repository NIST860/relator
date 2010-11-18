from django.db.models.fields.related import SingleRelatedObjectDescriptor
from django.db import models, router

class DataLinkDescriptor(SingleRelatedObjectDescriptor):
	def __get__(self, instance, instance_type=None):
		if instance is None:
			return self
		try:
			return getattr(instance, self.cache_name)
		except AttributeError:
			params = {'%s__pk' % self.related.field.name: instance._get_pk_val()}
			db = router.db_for_read(self.related.model, instance=instance)
			try:
				rel_obj = self.related.model._base_manager.using(db).get(**params)
			except self.related.model.DoesNotExist:
				rel_obj = self.related.model.get(instance)
			setattr(instance, self.cache_name, rel_obj)
			return rel_obj


class DataLinkField(models.OneToOneField):
	def __init__(self, to, related_name=None, to_field=None, **kwargs):
		kwargs.setdefault('primary_key', True)
		kwargs['related_name'] = related_name
		super(DataLinkField, self).__init__(to, to_field, **kwargs)

	def contribute_to_related_class(self, cls, related):
		setattr(cls, related.get_accessor_name(), DataLinkDescriptor(related))
