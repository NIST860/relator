import os
from itertools import chain
from locations.models import *
from standards.models import *
from structures.models import *
from carbon.models import *
from units import *
from results import Results
from quantities import markup, Quantity
markup.config.use_unicode = True

buildings = Building.objects.all()
locations = Location.objects.all()
standards = Standard.objects.all()
periods = ((10 * year), (25 * year), (40 * year))

file = open(os.path.join('scripts', 'output.xls'), 'a')
print >> file, '\t'.join(chain((
	'Building Type',
	'City',
	'State',
	'Study Period',
	'Standard',
	'Total LCC ($)',
	'Energy Efficiency Costs ($)',
	'Total Energy Costs ($)',
	'Total Energy Use (kWh)',
	'Gas BTU/yr (kft^3)',
	'Electricity BTU/yr (kWh)',
	'EPS',
), map(str, Impact.objects.all()), map(str, EmissionType.objects.all())))

def strip(value):
	return value.item() if isinstance(value, Quantity) else value
def format(value):
	return '%.15f' % float(strip(value))

start = ('A06', 'Moline', 'IL', '25', '2007')
started = False

exceptions = []
for building in buildings:
	for location in locations:
		for standard in standards:
			for year in periods:
				if not started:
					key = (building.pk, location.name, location.state.code, str(int(year.item())), standard.name)
					if key == start:
						started = True
					print building, location, standard, year
					continue
				try:
					r = Results(building, standard, location, year, 0.03)
					print >> file, '\t'.join(chain(map(str, (
							building.type,
							location.name,
							location.state,
							year.item(),
							standard.name,
						)), map(str, map(strip, (
							r.lifecycle.cost(),
							r.energy_efficiency.cost(),
							r.energy.cost(),
							r.energy.use(),
							r.energy.fuel('Gas').use,
							r.energy.fuel('Electric').use,
						))),
						['%.2f' % r.emissions.eps],
						map(format, r.emissions.impacts.values()),
						map(format, r.emissions.emissions.values())))
					print building, location, standard, year
				except Exception as e:
					exceptions.append((building, location, standard, year, e))
file.close()

errors = open(os.path.join('scripts', 'errors.txt'), 'w')
print >> errors, '\n'.join(map(str, exceptions))
errors.close()
raise
