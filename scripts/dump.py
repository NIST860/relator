import os
from itertools import chain
from carbon.models import Impact, EmissionType
from results.models import Row
from quantities import markup
markup.config.use_unicode = True

file = open(os.path.join('scripts', 'output.txt'), 'a')
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

for row in Row.objects.all():
	for cost in row.costs.all():
		print >> file, '\t'.join(map(str, chain((
			row.building.type,
			row.location.name,
			row.location.state.code,
			int(cost.period.item()),
			row.standard.name,
			cost.lifecycle_cost.item(),
			cost.efficiency_cost.item(),
			cost.energy_cost.item(),
			cost.energy_use.item(),
			cost.gas_use.item(),
			cost.electricity_use.item(),
			row.eps * int(cost.period.item())),
			((i.amount * cost.period).item() for i in row.impacts.all()),
			((e.amount * cost.period).item() for e in row.emissions.all()))))
		print row

file.close()
