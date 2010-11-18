from django.contrib import admin
from relator.carbon import models
from relator.admin import registerer

class EquivalenceInline(admin.TabularInline):
	model = models.Equivalence


class EmissionAdmin(admin.ModelAdmin):
	list_display = 'type', 'fuel', 'state'
	list_filter = 'type', 'fuel', 'state'


class EmissionTypeAdmin(admin.ModelAdmin):
	list_display = 'name', 'unit'
	list_editable = 'unit',
	inlines = [EquivalenceInline]


class ImpactAdmin(admin.ModelAdmin):
	inlines = [EquivalenceInline]


register = registerer()
register(models.EmissionType, EmissionTypeAdmin, advanced=True)
register(models.Emission, EmissionAdmin)
register(models.Impact, ImpactAdmin)
