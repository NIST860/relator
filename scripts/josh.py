from locations.models import Location
from standards.models import Standard
from structures.models import Building
from results.templatetags.comparison import delta, percent, airr
from results.comparison import Comparison
from quantities import year

building = Building.objects.get(pk='O03')
locations = Location.objects.filter(representative=True)
years = ((10 * year), (25 * year), (40 * year))

file = open('deltas.csv', 'w')
print >> file, ','.join(('Study Length', 'Location', '% Reduction LCC', '% Reduction Energy', 'AIRR'))
for location in locations:
	for year in years:
		standards = Standard.objects.filter(name__in=('2007', 'LEC'))
		c = Comparison(standards, building, location, year, '0.03')
		baseline = c.baseline()
		for results in c.rest():
			plc = percent(results.lifecycle.cost(), baseline.lifecycle.cost())
			pe = percent(results.energy.use(), baseline.energy.use())
			print >> file, ','.join(map(str, (
				year.item(),
				location.name,
				plc,
				pe,
				results.airr(baseline))))
			print location, year
		file.write('\n')
file.close()
