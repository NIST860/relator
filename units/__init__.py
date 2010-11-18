import quantities
from quantities import markup
from quantities.unitquantity import UnitCurrency

class Quantity(quantities.Quantity):
	def into(self, units):
		if getattr(self, '_units', False) == units:
			return self
		other = self * 1
		other.units = other._units = units
		return other

	def just(self, units):
		return self.into(units).item()

dollar = UnitCurrency('dollar', symbol='$',
		aliases=['dollars'])


def sum(args, initial=0 * dollar):
	from operator import add
	args = list(args)
	if len(args) is 0: return initial
	return reduce(add, args)
