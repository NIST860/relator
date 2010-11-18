from base import Results
from relator.units import sum, dollar

class Rates(Results):
	class Meta:
		abstract = True

	@classmethod
	def create(cls, component, parent):
		self = cls(parent=parent)
		period = parent.row.period
		group = parent.row.group
		mcost = component.maintenance_cost
		rcost = component.repair_cost
		rrate = component.repair_rate
		pcost = component.replacement_cost
		prate = component.replacement_rate
		year = parent.row.year
		pv = parent.row.pv

		self.maintenance = sum(pv(mcost, year) for year in parent.row.years)

		total = 0 * dollar
		replaced = 1
		for year in parent.row.years:
			if (year - replaced) >= prate:
				replaced = year
			if (year - replaced) >= rrate:
				total += pv(rcost, year)
		self.repair = total

		times = int((period // prate).item())
		self.replacement = sum(pv(pcost, prate * i) for i in range(1, times + 1))

		if period < prate:
			self.credit = 0 * dollar
		else:
			leftover = period % prate
			total = (leftover / prate) * pcost
			self.credit = pv(total, year)

		self.save()
		return self
