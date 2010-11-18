from django.template import Library
register = Library()


def airr(left, right):
	airr = left.airr(right)
	return ('%.4f' % airr) if isinstance(airr, float) else airr
register.filter(airr)


def delta(left, right):
	return left - right
register.filter(delta)


def percent(left, right):
	return ((1 - (left / right)) * 100).item()
register.filter(percent)


def div(left, right):
	return float(left) / right
register.filter(div)
