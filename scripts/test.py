from django.core.management import setup_environ
import settings
print setup_environ(settings)

import sys, os
from quantities import year
from django.db.transaction import commit_on_success
from locations.models import Location
from standards.models import Standard
from structures.models import Building
from carbon.models import Emission, Impact
from results.models import *
from database import models as db
from units import *
from results import Results
from quantities import markup, Quantity
markup.config.use_unicode = True

buildings = Building.objects.all()
locations = Location.objects.all()
standards = Standard.objects.all()
periods = [1 * year, 10 * year, 25 * year, 40 * year]
set = ResultSet.objects.get(deflator='0.03')
database = db.Database.get(deflator='0.03')
exceptions = []
carbon = None

def residual(cost):
	group = db.Group.get(
			database=database,
			location=cost.row.location,
			building=cost.row.building,
			standard=cost.row.standard)
	row = group.row_for(cost.period)
	return row.residual.cost

@commit_on_success
def alter(building, location, standard):
	sys.stdout.write('%s, %s, %s\n' % (building, location, standard))
	row = Row.objects.get(set=set, building=building, standard=standard, location=location)
	costs = row.costs.all()
	new = min(map(residual, costs))
	sys.stdout.write('\t')
	for cost in costs:
		r = Results(building, standard, location, cost.period, carbon, '0.03')
		old = r.base_residual.cost()
		cost.lifecycle_cost -= old
		cost.lifecycle_cost += new
		cost.save()
		sys.stdout.write('%d,' % int(cost.period.item()))
	sys.stdout.write('\nSuccess\n')

index = int(sys.argv[1]) if len(sys.argv) > 1 else 1
for location in locations:
	for standard in standards:
		alter(buildings[index], location, standard)
