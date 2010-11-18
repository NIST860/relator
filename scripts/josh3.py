from os import path
from locations.models import Location
from standards.models import Standard
from structures.models import Building
from results import Results
from quantities import year

buildings = Building.objects.all()
locations = Location.objects.all()
standards = Standard.objects.all()
periods = ((10 * year), (25 * year), (40 * year))

file = open(path.join('scripts', 'josh.csv'), 'w')

print >> file, ','.join((
	'Building Type',
	'City',
	'State',
	'Study Period',
	'Standard',
	'Total LCC',
	'Energy Efficiency Costs',
	'Total Energy Costs',
	'Total Energy Use',
	'Gas BTU/yr',
	'Electricity BTU/yr',
))

exceptions = []
for building in buildings:
	for location in locations:
		for standard in standards:
			for year in periods:
				try:
					r = Results(building, standard, location, year, 0.03)
					print >> file, ','.join(map(str, (
						building.type,
						location.name,
						location.state,
						year.item(),
						standard.name,
						r.lifecycle.cost(),
						r.energy_efficiency.cost(),
						r.energy.cost(),
						r.energy.use(),
						r.energy.fuel('Gas').use,
						r.energy.fuel('Electric').use,
					)))
					print building, location, standard, year
				except Exception as e:
					exceptions.append(e)
file.close()
errors = open(path.join('scripts', 'errors.txt'), 'w')
print >> errors, '\n'.join(exceptions)
errors.close()
