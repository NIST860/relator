from django import template
register = template.Library()

@register.filter
def fuel_use(data, fuel):
	return data.fuel_use(fuel)

@register.filter
def fuel_cost(data, fuel):
	return data.fuel_cost(fuel)
