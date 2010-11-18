import os
from quantities import year
from django.db.transaction import commit_on_success
from locations.models import Location
from standards.models import Standard
from structures.models import Building
from carbon.models import Emission, Impact
from units import *
from results import Results
from quantities import markup, Quantity
from database.models import *
markup.config.use_unicode = True

periods = [1 * year, 10 * year, 25 * year, 40 * year]
database = Database.get(deflator='0.03')
buildings = Building.objects.all()
locations = Location.objects.all()
standards = Standard.objects.all()
exceptions = []


@commit_on_success
def create(building, location, standard, period):
	try:
		group = Group.get(
				database=database,
				building=building,
				location=location,
				standard=standard)
		row = group.row_for(period)
		group.data.save()
		group.emission.save()
		row.data.save()
		row.residual.save()
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
