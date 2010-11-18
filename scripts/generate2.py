import os
from quantities import year
from django.db.transaction import commit_on_success
from locations.models import Location
from standards.models import Standard
from structures.models import Building
from carbon.models import Emission, Impact
from results.models import *
from units import *
from results import Results
from quantities import markup, Quantity
markup.config.use_unicode = True

buildings = Building.objects.all()
locations = Location.objects.all()
standards = Standard.objects.all()
periods = [1 * year, 10 * year, 25 * year, 40 * year]
deflator, marr = '0.03', '0.03'
set, _ = ResultSet.objects.get_or_create(deflator=deflator, marr=marr)
exceptions = []
carbon = None


@commit_on_success
def create(building, location, standard, period):
	try:
		if Costs.objects.filter(
				row__set=set,
				row__building=building,
				row__location=location,
				row__standard=standard,
				period=period).count():
			print 'skipping', building, location, standard
			return

		r = Results(building, standard, location, period, carbon, deflator, marr)

		try:
			row = Row.objects.get(set=set, building=building, location=location, standard=standard)
		except Row.DoesNotExist:
			row = Row.objects.create(set=set, building=building, location=location, standard=standard, eps=r.emissions.eps)
			for (impact, value) in r.emissions.impacts.items():
				Impact.objects.create(row=row, impact=impact, amount=value)
			for (emission, value) in r.emissions.emissions.items():
				Emission.objects.create(row=row, emission=emission, amount=value)

		Costs.objects.create(
			row=row,
			period=period,
			lifecycle_cost=r.lifecycle.cost(),
			efficiency_cost=r.energy_efficiency.cost(),
			energy_cost=r.energy.cost(),
			energy_use=r.energy.use(),
			gas_use=r.energy.fuel('Gas').use.into('BTU') / year,
			electricity_use=r.energy.fuel('Electric').use.into('BTU') / year)
		print building, location, standard, period
	except Exception as e:
		print 'broken', building, location, standard, period
		exceptions.append((building, location, standard, period, e))


for building in buildings:
	for location in locations:
		for standard in standards:
			for period in periods:
				create(building, location, standard, period)

errors = open(os.path.join('scripts', 'errors.txt'), 'w')
print >> errors, '\n'.join(map(str, exceptions))
errors.close()
print exceptions
if exceptions: raise exceptions[0][-1]
