from base import Results
from fields import DataLinkField
from relator.units import fields, dollar, sum

class GroupData(Results):
	group = DataLinkField('Group', 'data')
	esavings = fields.CostField()
	first = fields.CostField()

	def make(self, group):
		self.esavings = group.assemblies.delta + group.components.delta
		self.first = self.esavings + group.index(group.building.subtotal, 'weighted-average')
		self.save()


class Residual(Results):
	row = DataLinkField('Row', 'residual')
	cost = fields.CostField()

	def make(self, row):
		building = row.group.building
		if row.period > building.life:
			return 0 * dollar
		left = building.life - row.period
		self.cost = (float(left) / building.life.item()) * row.group.data.first
		self.save()


class RowData(Results):
	row = DataLinkField('Row', 'data')
	base = fields.CostField()
	future = fields.CostField(null=True)
	investment = fields.CostField(null=True)
	lifecycle = fields.CostField(null=True)
	maintenance = fields.CostField(null=True)
	repair = fields.CostField(null=True)
	replacement = fields.CostField(null=True)
	credit = fields.CostField(null=True)

	def make(self, row):
		building = row.group.building
		spv = row.group.database.spv
		cost = lambda year: building.costs.get(year=year).cost
		base = building.square_feet * sum(cost(year) * spv(year) for year in row.years)
		self.base = row.group.index(base, 'whitestone')
		self.save()
		parts = row.assemblies, row.components
		for attr in 'maintenance', 'repair', 'replacement', 'credit':
			setattr(self, attr, sum(getattr(part, attr) for part in parts))

		residual = min(r.residual.cost for r in row.options)
		self.future = row.pv(
				row.energy.cost
				+ self.base
				+ self.maintenance
				+ self.repair
				+ self.replacement
				- self.credit
				- residual)

		self.investment = (
				row.group.data.first
				- residual
				+ self.replacement)

		self.lifecycle = (row.group.data.first + self.future)
		self.save()
