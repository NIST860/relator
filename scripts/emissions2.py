import os, sys
from locations.models import *
from standards.models import *
from structures.models import *
from results import Results
from units import *
year = Quantity(1, 'year')
building = Building.objects.get(pk='A03')
standard = Standard.objects.get(name='LEC')
location = Location.objects.get(name='Anchorage')
r = Results(building, standard, location, year, '0.03')


file = open(os.path.join('scripts', 'ANCHORAGE-LEC.txt'), 'w')
print >> file, building, standard, location
print >> file, r.emissions.eps
print >> file, 'Normalized:'
for k, v in r.emissions.normalized.items():
	print >> file, '\t', k, '\n\t\t', v, 'capita years'
print >> file, 'Impacts:'
for k, v in r.emissions.impacts.items():
	print >> file, '\t', k, '\n\t\t', v
print >> file, 'Emissions:'
for k, v in r.emissions.emissions.items():
	print >> file, '\t', k, '\n\t\t', v
file.close()


standard = Standard.objects.get(year=2007)
r = Results(building, standard, location, year, '0.03')

file = open(os.path.join('scripts', 'ANCHORAGE-2007.txt'), 'w')
print >> file, building, standard, location
print >> file, r.emissions.eps
print >> file, 'Normalized:'
for k, v in r.emissions.normalized.items():
	print >> file, '\t', k, '\n\t\t', v, 'capita years'
print >> file, 'Impacts:'
for k, v in r.emissions.impacts.items():
	print >> file, '\t', k, '\n\t\t', v
print >> file, 'Emissions:'
for k, v in r.emissions.emissions.items():
	print >> file, '\t', k, '\n\t\t', v
file.close()
