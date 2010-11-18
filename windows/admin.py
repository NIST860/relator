from django.contrib import admin
from relator.windows import models
from relator.admin import registerer, structure

class ASHRAEWindowAdmin(admin.ModelAdmin):
	list_display = 'obj', 'u_factor', 'shgc', 'vt'

	def obj(self, obj):
		return unicode(obj)


class RSMeansWindowAdmin(admin.ModelAdmin):
	search_fields = 'description',


class WindowAdditionAdmin(admin.ModelAdmin):
	list_display = 'name', 'cost'
	list_editable = 'cost',
	search_fields = 'name',


class WindowModifierAdmin(admin.ModelAdmin):
	list_display = 'name', 'rate'
	list_editable = 'rate',
	search_fields = 'name',


register = registerer(structure)

register(models.Direction, advanced=True)
register(models.Operability, advanced=True)
register(models.Frame, advanced=True)
register(models.Film, advanced=True)

register(models.ASHRAEWindow, ASHRAEWindowAdmin)
register(models.RSMeansWindow, RSMeansWindowAdmin)
register(models.WindowModifier, WindowModifierAdmin)
