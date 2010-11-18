import quantities as q
from django import template
from django.contrib.humanize.templatetags.humanize import intcomma
from relator.units import dollar, Quantity
register = template.Library()

def price(val):
	if val == '':
		return val
	elif isinstance(val, Quantity):
		val = val.just(dollar)
	elif isinstance(val, q.Quantity):
		val = val * 1
		val.units = dollar
		val = val.item()
	head, tail = ('%.2f' % float(val)).split('.')
	return '${0}.{1}'.format(intcomma(head), tail)
register.filter(price)


def costdiff(val):
	val.units = dollar
	val = val.item()
	(prefix, val) = ('-', -val) if val < 0 else ('+', val)
	head, tail = ('%.2f' % float(val)).split('.')
	return '{0}${1}.{2}'.format(prefix, intcomma(head), tail)
register.filter(costdiff)


def costpsqft(val):
	from quantities import ft
	val.units = 'dollar / ft**2'
	val = val.item()
	(prefix, val) = ('-', -val) if val < 0 else ('+', val)
	head, tail = ('%.2f' % float(val)).split('.')
	return u'{0}${1}.{2}/ft\xB2'.format(prefix, intcomma(head), tail)
register.filter(costpsqft)


@register.filter
def name(obj):
	return obj._meta.verbose_name


@register.filter
def grade(num):
	grades = ('A', 'C', 'X', 'U')
	return 'grade%s' % (grades[int(num) % len(grades)])


@register.filter
def by(iter, n):
	items = list(iter)
	for i in range(0, len(items), n):
		yield items[i:i+n]


@register.filter
def item(q, units=None):
	if units:
		q = q * 1
		q.units = units
	return q.item()
