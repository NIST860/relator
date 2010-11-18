from django.contrib import admin
from relator.constants import models
from relator.admin import registerer, basic


class PriceIndexAdmin(admin.ModelAdmin):
	list_display = 'fuel', 'year', 'zone', 'value'
	list_editable = 'value',
	list_filter = 'fuel', 'zone', 'year'


class TariffAdmin(admin.ModelAdmin):
	list_display = 'state', 'fuel', 'tariff'
	list_filter = 'fuel',


register = registerer(basic)
register(models.PriceIndex, PriceIndexAdmin)
register(models.Tariff, TariffAdmin)
register(models.MRRRates)
