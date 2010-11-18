import os
from quantities import *
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
standards = Standard.objects.filter(year=1999)
periods = [p * year for p in (10, 25, 40)]
deflator, marr = '0.03', None
set, _ = ResultSet.objects.get_or_create(deflator=deflator, marr=marr)
exceptions = []


@commit_on_success
def create(building, location, standard, period):
	try:
		r = Results(building, standard, location, period, deflator, marr)
		Base.objects.create(building=building, location=location, period=period, residual=r.base.residual.cost())
	except Exception as e:
		print 'broken', building, location, standard, period
		exceptions.append((building, location, standard, period, e))
		raise


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
