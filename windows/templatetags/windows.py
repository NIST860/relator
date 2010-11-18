from django import template
register = template.Library()

@register.filter
def window(data, d):
	return data.window(d)

@register.filter
def window_area(data, d):
	return data.window_area(d)

@register.filter
def delta_window_cost(data, d):
	return data.delta_window_cost(d)
