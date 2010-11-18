
import os
from locations.models import *
from standards.models import *
from structures.models import *
from results import Results
from units import *

year = Quantity(10, 'years')
building = Building.objects.get(pk='A03')
standard = Standard.objects.get(name='LEC')
location = Location.objects.get(name='Anchorage')
r = Results(building, standard, location, year, '0.03')
print r.energy.fuel('electric').use
print r.energy.fuel('electric').use.into('BTU')
for (k, v) in r.emissions.impacts.items():
	print k, v
	state = r.location.state
	usage = r.energy.usage
	years = r.year
	for equivalence in k.equivalences.select_related('type'):
		type, eq = equivalence.emission, equivalence.equivalence
		print '\t', type, (type.total(state, usage, years) * eq)

raise Exception
