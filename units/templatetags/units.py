from django import template
register = template.Library()

@register.simple_tag
def use_unicode():
	from quantities import markup
	markup.config.use_unicode = True
	return ''


@register.filter
def delta_assembly_cost(data, assembly):
	return data.delta_assembly_cost(assembly)
