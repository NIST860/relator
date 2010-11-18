from django import template
register = template.Library()

@register.filter
def rates(system, zone):
	return system.rates(zone)


@register.filter
def delta_assembly_cost(data, assembly):
	return data.delta_assembly_cost(assembly)
