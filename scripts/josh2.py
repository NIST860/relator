import os, sys
from itertools import chain
from zones.models import CensusZone
from locations.models import Location
from standards.models import Standard
from structures.models import Building
from results.templatetags.comparison import delta, percent
from utilities.templatetags.utils import price
from results import Results
from quantities import year, markup
markup.config.use_unicode = False

building = Building.objects.get(pk='O03')
standards = Standard.objects.filter(name__in=('2007', 'LEC'))
locations = Location.objects.filter(representative=True)
years = ((10 * year), (25 * year), (40 * year))

for location in Location.objects.filter(name='Anchorage'):
	for standard in standards:
		for year in years:
			file = open(os.path.join('scripts', 'output', '%s-%s-%s-%s.txt' % (
				building.pk,
				location.name,
				standard.name,
				year.item())), 'w')
			r = Results(building, standard, location, year, '0.03')

			print >> file, 'Lifecycle:', price(r.lifecycle.cost())
			print >> file, 'Investment:', price(r.investment.cost())
			print >> file, '---------------------------------------------'

			###########################
			# First
			print >> file, 'First Costs:', price(r.first.cost())
			print >> file, '\tDelta Energy Efficiency:', price(r.energy_efficiency.delta())
			print >> file, '\tBuilding Subtotal:', price(r.first.index(r.building.subtotal, 'weighted-average'))
			###########################
			# Components
			print >> file, '\tComponent:', price(r.components.cost())
			print >> file, '\t\tInsulation:', price(r.components.insulation.cost())
			print >> file, '\t\t\tWall:', price(r.components.insulation.wall.cost())
			for sheet in iter(r.components.insulation.wall):
				print >> file, '\t\t\t\t%s' % sheet.component
			print >> file, '\t\t\tRoof:', price(r.components.insulation.roof.cost())
			for sheet in iter(r.components.insulation.roof):
				print >> file, '\t\t\t\t%s' % sheet.component
			print >> file, '\t\tWindows:', price(r.components.windows.cost())
			print >> file, '\t\tLighting:', price(r.components.lighting.cost())
			print >> file, '\t\t\tOverhang:', price(r.components.lighting.overhang.cost())
			print >> file, '\t\t\tDaylighting:', price(r.components.lighting.daylighting.cost())

			###########################
			# Assemblies
			print >> file, '\tAssembly:', price(r.assemblies.cost())
			for ac in iter(r.assemblies):
				print >> file, '\t\t', ac.assembly

			###########################
			# Energy
			print >> file, 'Energy:', price(r.energy.cost())
			print >> file, 'Use:', r.energy.use()
			for fuel in iter(r.energy):
				print >> file, '\t', fuel.fuel
				print >> file, '\t\t', price(fuel.cost())
				print >> file, '\t\t', fuel.use

			###########################
			# Future
			print >> file, 'Future Costs:', price(r.future.cost())
			print >> file, '\tResidual:', price(r.residual.cost())

			###########################
			# MRR
			print >> file, '\tMRR:'
			print >> file, '\t\tBase:', price(r.mrr.base.cost())
			# Maintenance
			print >> file, '\t\tMaintenance:', price(r.mrr.maintenance.cost())
			print >> file, '\t\t\tComponent:', price(r.components.maintenance())
			print >> file, '\t\t\t\tInsulation:', price(r.components.insulation.maintenance())
			print >> file, '\t\t\t\t\tWall:', price(r.components.insulation.wall.maintenance())
			print >> file, '\t\t\t\t\tRoof:', price(r.components.insulation.roof.maintenance())
			print >> file, '\t\t\t\tWindow:', price(r.components.windows.maintenance())
			print >> file, '\t\t\t\tLighting:', price(r.components.lighting.maintenance())
			print >> file, '\t\t\t\t\tOverhang:', price(r.components.lighting.overhang.maintenance())
			print >> file, '\t\t\t\t\tDaylighting:', price(r.components.lighting.daylighting.maintenance())
			print >> file, '\t\t\tAssembly:', price(r.assemblies.maintenance())
			for c in chain(*iter(r.assemblies)):
				print >> file, '\t\t\t\t', c.component, ': ', price(c.maintenance())
			# Repair
			print >> file, '\t\tRepair:', price(r.mrr.repair.cost())
			print >> file, '\t\t\tComponent:', price(r.components.repair())
			print >> file, '\t\t\t\tInsulation:', price(r.components.insulation.repair())
			print >> file, '\t\t\t\t\tWall:', price(r.components.insulation.wall.repair())
			print >> file, '\t\t\t\t\tRoof:', price(r.components.insulation.roof.repair())
			print >> file, '\t\t\t\tWindow:', price(r.components.windows.repair())
			print >> file, '\t\t\t\tLighting:', price(r.components.lighting.repair())
			print >> file, '\t\t\t\t\tOverhang:', price(r.components.lighting.overhang.repair())
			print >> file, '\t\t\t\t\tDaylighting:', price(r.components.lighting.daylighting.repair())
			print >> file, '\t\t\tAssembly:', price(r.assemblies.repair())
			for c in chain(*iter(r.assemblies)):
				print >> file, '\t\t\t\t', c.component, ': ', price(c.repair())
			# Replace
			print >> file, '\t\tReplace:', price(r.mrr.replacement.cost())
			print >> file, '\t\t\tComponent:', price(r.components.replacement())
			print >> file, '\t\t\t\tInsulation:', price(r.components.insulation.replacement())
			print >> file, '\t\t\t\t\tWall:', price(r.components.insulation.wall.replacement())
			print >> file, '\t\t\t\t\tRoof:', price(r.components.insulation.roof.replacement())
			print >> file, '\t\t\t\tWindow:', price(r.components.windows.replacement())
			print >> file, '\t\t\t\tLighting:', price(r.components.lighting.replacement())
			print >> file, '\t\t\t\t\tOverhang:', price(r.components.lighting.overhang.replacement())
			print >> file, '\t\t\t\t\tDaylighting:', price(r.components.lighting.daylighting.replacement())
			print >> file, '\t\t\tAssembly:', price(r.assemblies.replacement())
			for c in r.assemblies:
				print >> file, '\t\t\t\t', c.assembly, ': ', price(c.replacement())
			# Credit
			print >> file, '\t\tCredit:', price(r.mrr.credit.cost())
			print >> file, '\t\t\tComponent:', price(r.components.credit())
			print >> file, '\t\t\t\tInsulation:', price(r.components.insulation.credit())
			print >> file, '\t\t\t\t\tWall:', price(r.components.insulation.wall.credit())
			print >> file, '\t\t\t\t\tRoof:', price(r.components.insulation.roof.credit())
			print >> file, '\t\t\t\tWindow:', price(r.components.windows.credit())
			print >> file, '\t\t\t\tLighting:', price(r.components.lighting.credit())
			print >> file, '\t\t\t\t\tOverhang:', price(r.components.lighting.overhang.credit())
			print >> file, '\t\t\t\t\tDaylighting:', price(r.components.lighting.daylighting.credit())
			print >> file, '\t\t\tAssembly:', price(r.assemblies.credit())
			for c in chain(*iter(r.assemblies)):
				print >> file, '\t\t\t\t', c.component, ': ', price(c.credit())

			print file.name
			file.close()
