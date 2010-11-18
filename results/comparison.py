from relator.utilities.decorators import cached_property
from relator.results import Results

class Comparison(list):
	def __init__(self, standards, building, location, year,
			carbon=None, deflator='0.03', marr=None):
		self.building, self.location = building, location
		self.year, self.deflator = year, deflator
		self.marr = marr or deflator
		self.carbon = carbon
		if location.standard:
			self.standards = standards.filter(year__gte=location.standard.year)
		else:
			self.standards = standards

	@cached_property
	def results(self):
		return list(Results(
			self.building,
			standard,
			self.location,
			self.year,
			self.carbon,
			self.deflator,
			self.marr) for standard in self.standards.order_by('year'))

	def baseline(self):
		return self.results[0]

	def rest(self):
		return self.results[1:]
