import sys
from units import sum
from quantities import year
from itertools import chain
from locations.models import Location
from standards.models import Standard
from structures.models import Building
from database.models import *

def output(STATE_BASE=False):
	def strsin(args):
		return any(map(lambda s: isinstance(s, str), args))

	def med(args):
		return 'indeterminate' if strsin(args) else float(sum(args)) / len(args)

	periods = [1 * year, 10 * year, 25 * year, 40 * year]
	database = Database.get(deflator='0.03')
	s04 = Standard.objects.get(year=2004)
	s99 = Standard.objects.get(year=1999)
	file = open('scripts\\final-statebase.txt', 'w') if STATE_BASE else open('scripts\\final-2004base.txt', 'w')
	averages = {}

	outputs = (
		'%Delta Lifecycle Cost',
		'%Delta Energy Use',
		'%Delta Energy Cost',
		'%Delta Carbon Emissions',
		'AIRR')

	header = '\t'.join((
		'Location',
		'State',
		'Building',
		'Year',
		'Base',
		'Standard',
		'State Minimum',) + outputs)
	print >> file, header

	def base(location):
		year = (location.standard or s99).year if STATE_BASE else 2004
		return Standard.objects.get(year=year)

	def standards(location):
		year = (location.standard or s99).year if STATE_BASE else 2004
		if STATE_BASE:
			return Standard.objects.exclude(year=year)
		return Standard.objects.filter(year__gt=year)

	def output(building, location):
		oldgroup = Group.objects.get(
			database=database,
			building=building,
			location=location,
			standard=base(location))
		oldcarbon = oldgroup.emission.emission_set.get(type__pk=1).amount

		for standard in standards(location):
			group = Group.get(
				database=database,
				building=building,
				location=location,
				standard=standard)
			carbon = group.emission.emission_set.get(type__pk=1).amount

			for period in periods:
				year = period.item()
				new = group.row_for(period)
				old = oldgroup.row_for(period)

				dlcc = (1 - (new.data.lifecycle / old.data.lifecycle)).item() * 100
				deu = (1 - (new.energy.use / old.energy.use)).item() * 100
				dec = (1 - (new.energy.cost / old.energy.cost)).item() * 100
				dce = (1 - ((carbon * year) / (oldcarbon * year))).item() * 100
				t = (1.0 / year)
				top = (new.energy.cost - old.energy.cost)
				bottom = (group.data.esavings - oldgroup.data.esavings)
				if top == 0 and bottom == 0:
					airr = 0
				elif top < 0 and bottom <= 0:
					airr = 'indeterminate'
				elif top < 0 and bottom > 0:
					airr = '-infinity'
				elif top > 0 and bottom <= 0:
					airr = 'infinity'
				else:
					sir = (top / bottom).item()
					airr = (1 + 0.03) * (sir ** t) - 1
				results = (dlcc, deu, dec, dce, airr)
				print >> file, '\t'.join(map(str, chain(
					(location.name,
					 location.state.code,
					 building.type,
					 year,
					 oldgroup.standard.name,
					 standard.name,
					 standard == location.standard),
					 results)))
				key = (building.type, standard.year, year)
				lists = averages.setdefault(key, [[], [], [], [], []])
				for (r, rlist) in zip(results, lists):
					rlist.append(r)
				print location, building, standard, year

	for building in Building.objects.all():
		for location in Location.objects.all():
			output(building, location)

	print >> file, ''
	print >> file, '\t'.join(('Building', 'Standard', 'Year', 'Type', 'Min', 'Max', 'Median'))
	for ((b, s, y), lists) in averages.items():
		for (type, rlist) in zip(outputs, lists):
			print >> file, '\t'.join(map(str, (b, s, y, type, min(rlist), max(rlist), med(rlist))))

	file.close()
