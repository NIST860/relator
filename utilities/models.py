from django.db import models

class Type(models.Model):
	name = models.CharField(max_length=50)

	class Meta:
		abstract = True
		ordering = 'name',

	def __unicode__(self):
		return self.name.title()
