from relator.assemblies.models import Fuel
from relator.structures.models import Building
from relator.standards.models import Standard
from relator.locations.models import State, Location
from relator.data.models import EnergyPlusData
from relator.energy.models import FuelData
from relator.units import Quantity
import os, csv

root = os.path.join('energy', 'data')
electric = Fuel.objects.get(name='Electric')
gas = Fuel.objects.get(name='Gas')
convert = lambda cell: Quantity(float(cell.strip()), 'joules')
okgo = False

def locate_eplus(filename):
	building, location, standard = filename[:-9].split('-')
	print building, location, standard
	building = Building.objects.get(type=building)
	standard = Standard.objects.get(name=standard)
	state, location = location[4:6], location[7:]
	state = State.objects.get(code=state)
	name = location.replace('_', ' ').title()
	if name == 'Worchester': name = 'Worcester'
	try:
		location = Location.objects.get(state=state, name__iexact=name)
	except Location.DoesNotExist:
		location = Location.objects.get(state=state, name__istartswith=name.split(' ')[0])
	return EnergyPlusData.objects.get(location=location, building=building, standard=standard)

def dropfirst(iterator):
	next(iterator)
	return iterator

def acceptable(name):
	if not name.endswith('Meter.csv'):
		return False
	if name.startswith('.'):
		return False
	return name.count('-') == 2

for filename in filter(acceptable, os.listdir(root)):
	eplus = locate_eplus(filename)
	if eplus.building.pk == 'A03' and eplus.standard.year == 2007 and eplus.location.name == 'Phoenix':
		okgo = True
	if not okgo:
		continue
	file = open(os.path.join(root, filename))
	rows = dropfirst(csv.reader(file))
	for (hour, row) in enumerate(rows):
		FuelData.objects.get_or_create(eplus=eplus, fuel=electric, hour=hour, use=convert(row[17]))
		FuelData.objects.get_or_create(eplus=eplus, fuel=gas, hour=hour, use=convert(row[19]))
	file.close()
