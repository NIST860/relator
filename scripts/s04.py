from django.core.exceptions import ObjectDoesNotExist
from units import sum
from itertools import chain
from locations.models import Location
from standards.models import Standard
from structures.models import Building
from results.models import *

file = open('scripts\\2004-base.txt', 'w')
deflator = 0.03
averages = {}

def med(args):
	return float(sum(args)) / len(args)

outputs = (
	'%Delta Lifecycle Cost',
	'%Delta Energy Use',
	'%Delta Energy Cost',
	'%Delta Carbon Emissions',
	'AIRR')

print >> file, '\t'.join((
	'Location',
	'State',
	'Building',
	'Year',
	'Base',
	'Standard',
	'State Minimum',) + outputs)

averages = {}
s04 = Standard.objects.get(year=2004)

for building in Building.objects.all():
	for location in Location.objects.all():
		try:
			oldrow = Row.objects.get(building=building, location=location, standard=s04)
			oldcarbs = oldrow.emissions.get(emission__pk=1).total
			for standard in Standard.objects.filter(year__gt=2004):
				newrow = Row.objects.get(building=building, location=location, standard=standard)
				newcarbs = newrow.emissions.get(emission__pk=1).total
				for new in newrow.costs.all():
					year = new.period.item()
					old = oldrow.costs.get(period=new.period)
					dlcc = (1 - (new.lifecycle_cost / old.lifecycle_cost)) * 100
					deu = (1 - (new.energy_use / old.energy_use)) * 100
					dec = (1 - (new.energy_cost / old.energy_cost)) * 100
					dce = (1 - ((newcarbs * year) / (oldcarbs * year))) * 100
					t = (1.0 / year)
					top = (new.energy_cost - old.energy_cost)
					bottom = (new.efficiency_cost - old.efficiency_cost)
					sir = -1 if bottom <= 0 else (top / bottom).item()
					airr = float('infinity') if sir < 0 else ((1 + deflator) * (sir ** t) - 1)
					results = (dlcc, deu, dec, dce, airr)
					print >> file, '\t'.join(map(str, chain(
						(location.name,
							location.state.code,
							building.type,
							year,
							oldrow.standard.name,
							standard.name,
							standard == location.standard),
						results)))
					key = (building.type, standard.year, year)
					lists = averages.setdefault(key, [[], [], [], [], []])
					for (r, rlist) in zip(results, lists):
						rlist.append(r)
					print location, building, standard, year
		except ObjectDoesNotExist:
			pass

print >> file, ''
print >> file, '\t'.join(('Building', 'Standard', 'Year', 'Type', 'Min', 'Max', 'Median'))
for ((b, s, y), lists) in averages.items():
	for (type, rlist) in zip(outputs, lists):
		print >> file, '\t'.join(map(str, (b, s, y, type, min(rlist), max(rlist), med(rlist))))

file.close()
