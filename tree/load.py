import os, sys
from quantities import W, J
from relator.tree.models import *
from assemblies.models import Fuel

class FileNotFound(ValueError):
	pass

gas = Fuel.objects.get(name='Gas')
electric = Fuel.objects.get(name='Electric')
exceptions = []

root = "X:\\Josh\\SURF - Tree Shading\\"

def getter(location, age, x, y):
	base = os.path.join(root, location, str(age))
	filename = os.path.join(base, 'house and tree %d-%d %d year{0}.csv' % (x, y, age))
	if not os.path.exists(filename.format('')):
		raise FileNotFound(filename.format(''))
	return lambda suffix='': open(filename.format(suffix))


def load_use(get, tree):
	rows = get('Meter')
	header = next(rows)
	one, two = next(rows), next(rows)
	for (month, days) in enumerate((
			range(31), # January
			range(28), # February
			range(31), # March
			range(30), # April
			range(31), # May
			range(30), # June
			range(31), # July
			range(31), # August
			range(30), # September
			range(31), # October
			range(30), # November
			range(31), # December
		)):
		e = EnergyUse(tree=tree, month=month, fuel=electric, use=0 * J)
		g = EnergyUse(tree=tree, month=month, fuel=gas, use=0 * J)
		for day in days:
			d, eu, gu = next(rows).split(',')
			e.use += float(eu) * J
			g.use += float(gu) * J
		e.save()
		g.save()
	rows.close()


def load_peak(get, tree):
	file = get('Table')
	me, mg = list(file)[28].split(',')[2:4]
	PeakDemand.objects.create(tree=tree, fuel=electric, max=float(me) * W)
	PeakDemand.objects.create(tree=tree, fuel=gas, max=float(mg) * W)
	file.close()


def load(location, age, x, y):
	get = getter(location, age, x, y)
	Snapshot.objects.filter(location=location, age=age, x=x, y=y).delete()
	tree = Snapshot.objects.create(location=location, age=age, x=x, y=y)
	load_peak(get, tree)
	load_use(get, tree)

def loadin(location, age):
	for i in list(range(16)):
		for j in list(range(16)):
			i, j = i * 7, j * 7
			if Snapshot.objects.filter(location=location, age=age, x=i, y=j).count():
				print 'already did', i, j
				continue
			try:
				load(location, age, i, j)
			except FileNotFound as e:
				sys.stdout.write('.')
			except Exception as e:
				exceptions.append(e)
			else:
				print location, age, i, j

def loadfrom(location):
	for age in range(2, 43):
		loadin(location, age)


def loadall():
	map(loadfrom, ('Sacramento', 'Boulder', 'DC', 'Miami', 'Phoenix', 'StLouis'))

loadall()

errors = open('errors.txt', 'w')
print >> errors, '\n'.join(map(str, exceptions))
errors.close()
print exceptions
