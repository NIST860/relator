import sys, os, re
from django.db import transaction
from relator.assemblies.models import Fuel
from relator.structures.models import Building
from relator.standards.models import Standard
from relator.locations.models import State, Location
from relator.windows.models import Direction
from relator.data.models import FuelEndUse, WindowRatio, SkylightRatio, WindowData, EnergyPlusData
from BeautifulSoup import BeautifulSoup

root = os.path.join('data', 'html')
td = re.compile('<td align="right">\s*(\d+\.\d+)</td>')


def locate_models(filename):
	building, location, standard = filename[:-10].split('-')
	building = Building.objects.get(type=building)
	standard = Standard.objects.get(name=standard)
	state, location = location[4:6], location[7:]
	state = State.objects.get(code=state)
	name = location.replace('_', ' ').title()
	try:
		location = Location.objects.get(state=state, name__iexact=name)
	except Location.DoesNotExist:
		location = Location.objects.get(state=state, name__istartswith=name.split(' ')[0])
	return location, building, standard


def locate_eplus(filename):
	building, location, standard = filename[:-10].split('-')
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


def enduse_values(soup):
	t = soup.find(name='b', text='End Uses').findNext('table')
	rows = t.findChildren('tr')
	h, c, t = rows[1], rows[2], rows[16]
	he, hg = [float(td.text) for td in h.findChildren('td')[1:3]]
	ce, cg = [float(td.text) for td in c.findChildren('td')[1:3]]
	te, tg = [float(td.text) for td in t.findChildren('td')[1:3]]
	return he, hg, ce, cg, te, tg


def capacity_values_easy(soup):
	t = soup.find(name='b', text='Central Plant').findNext('table')
	if len(t.findChildren('tr')) < 3:
		return None, None
	cr, hr = t.findChildren('tr')[1:3]
	return cr.findChildren('td')[1].text, hr.findChildren('td')[1].text


def capacity_values_hard(soup):
	ct = soup.find(name='b', text='Central Plant').findNext('table').findNext('table')
	ht = ct.findNext('table')
	def getsum(t):
		rows = (r.findChildren('td') for r in t.findChildren('tr')[1:])
		return sum(float(row[2].text) for row in rows)
	return getsum(ct), getsum(ht)


def building_area(soup):
	b = soup.find(name='b', text='Building Area').findParent()
	t = b.findNext('table')
	row = t.findChildren('tr')[1]
	return float(row.findChildren('td')[1].text)


def window_ratio(soup):
	t = soup.find(name='b', text='Window-Wall Ratio').findNext('table')
	wallr, windowr = t.findChildren('tr')[1:3]
	wall = float(wallr.findChildren('td')[1].text)
	window = float(windowr.findChildren('td')[1].text)
	return wall, window


def skylight_ratio(soup):
	t = soup.find(name='b', text='Skylight-Roof Ratio').findNext('table')
	roofr, skylightr = t.findChildren('tr')[1:3]
	roof = float(roofr.findChildren('td')[1].text)
	skylight = float(skylightr.findChildren('td')[1].text)
	return roof, skylight


def fenestration(soup):
	t = soup.find(text='Fenestration').findNext('table')
	rows = t.findChildren('tr')[1:-3]
	def get(o):
		row = filter(lambda row: row.findChild(text=o), rows)[0]
		return [float(td.text) for td in row.findChildren('td')[3:7]]
	return map(get, 'NSWE')


peak = re.compile(r'name="?COMPONENTSOFPEAKELECTRICALDEMAND::Meter"?')
maxm = re.compile(r'Maximum of Months')
def max_electricity(lines):
	on, count = False, 0
	for (i, line) in enumerate(lines):
		if peak.search(line):
			on = True
			continue
		if not on:
			continue
		if maxm.search(line):
			return float(td.search(lines[i+2]).groups()[0])


shading = re.compile('FIXED SHADING')
def overhang_area(lines):
	on, values = False, []
	for (i, line) in enumerate(lines):
		if on:
			values.append(td.search(line).groups()[0])
			on = False
		elif shading.search(line):
			on = True
	return sum(map(float, values))


def load(filename):
	sid = transaction.savepoint()
	try:
		file = open(os.path.join(root, filename))
		lines = list(file)
		print 'going in'
		maxelectricity = max_electricity(lines)
		print 'out, mf'
		overhangarea = overhang_area(lines)
		file.close()

		location, building, standard = locate_models(filename)
		if EnergyPlusData.objects.filter(location=location, building=building, standard=standard).count():
			sys.stdout.write('.')
			transaction.savepoint_commit(sid)
			return

		soup = BeautifulSoup(open(os.path.join(root, filename)))

		he, hg, ce, cg, te, tg = enduse_values(soup)

		cr, hr = capacity_values_easy(soup)
		if cr is None or hr is None:
			cr2, hr2 = capacity_values_hard(soup)
		cooling_capacity, heating_capacity = cr or cr2, hr or hr2
		area = building_area(soup)

		n, s, w, e = fenestration(soup)

		print '\n'.join(map(str, (
			location, building, standard,
			heating_capacity, cooling_capacity, area,
			maxelectricity, overhangarea)))

		eplus = EnergyPlusData.objects.create(
				location=location, building=building, standard=standard,
				heating_capacity=heating_capacity, cooling_capacity=cooling_capacity,
				area=area, max_electricity=maxelectricity, overhang_area=overhangarea)

		FuelEndUse.objects.create(
				eplus=eplus, fuel=Fuel.objects.get(name='Electric'),
				heating=he, cooling=ce, total=te)
		FuelEndUse.objects.create(
				eplus=eplus, fuel=Fuel.objects.get(name='Gas'),
				heating=hg, cooling=cg, total=tg)

		wall, window = window_ratio(soup)
		WindowRatio.objects.create(eplus=eplus, gross=wall, opening=window)

		roof, skylight = skylight_ratio(soup)
		SkylightRatio.objects.create(eplus=eplus, gross=roof, opening=skylight)

		for (dir, data) in zip(Direction.objects.order_by('name'), (e, n, s, w)):
			WindowData.objects.create(eplus=eplus, direction=dir, area=data[0], u_value=data[1], shgc=data[2], vt=data[3])

		sys.stdout.write('.')
		transaction.savepoint_commit(sid)
	except Exception as e:
		print '\nERROR:', filename, e
		transaction.savepoint_rollback(sid)
		raise


def update(filename):
	try:
		data = locate_eplus(filename)
		print filename, data.pk
	except EnergyPlusData.DoesNotExist:
		print filename
		return load(filename)
	except Exception as e:
		print filename
		raise
	file = open(os.path.join(root, filename))
	data.overhang_area = overhang_area(line for line in file)
	data.save()


def reload(filename):
	try:
		locate_eplus(filename)
	except EnergyPlusData.DoesNotExist:
		load(filename)
	else:
		print 'skipping', filename


def files():
	return filter(lambda s: s.count('-') is 2 and s.endswith('.html'), os.listdir(root))


def loadall():
	map(load, files())


def updateall():
	map(update, files())


def reloadall():
	map(reload, files())
