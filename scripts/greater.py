from django.db.models import Sum
from data.models import EnergyPlusData
from standards.models import Standard
from assemblies.models import Fuel
bases = {}
s99 = Standard.objects.get(year=1999)
file = open('scripts\\errors.txt', 'w')
datasets = EnergyPlusData.objects.annotate(use=Sum('fuel_enduses__total'))
offenders = []

def broken():
	for eplus in datasets.filter(standard__year__gt=1999):
		key = (eplus.building.pk, eplus.location.pk, eplus.standard.pk)
		if key not in bases:
			bases[key] = datasets.get(building=eplus.building, location=eplus.location, standard=s99)
		base = bases[key]
		if base.use < eplus.use:
			yield (eplus, base.use, eplus.use)
		if eplus.standard.year == 2001 and base.use != eplus.use:
			offenders.append((eplus, base.use, eplus.use))

for eplus, old, new in broken():
	print >> file, '%s - %s - %s: from %s to %s' % (eplus.building, eplus.location, eplus.standard, old, new)

if offenders:
	print >> file, 'ERROR - 2001 / 1999 mismatch'
for eplus, old, new in offenders:
	print >> file, '%s - %s - %s: from %s to %s' % (eplus.building, eplus.location, eplus.standard, old, new)

file.close()
