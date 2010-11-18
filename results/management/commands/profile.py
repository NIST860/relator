from django.core.management.base import BaseCommand

class Command(BaseCommand):
	def handle(self, *args, **options):
		import cProfile as profile
		from results import Results
		from locations.models import Location
		from standards.models import Standard
		from structures.models import Building
		from units import Quantity
		l = Location.objects.all()[0]
		s = Standard.objects.all()[0]
		b = Building.objects.all()[0]
		y = Quantity(40, 'years')
		d = 0.03
		profile.runctx('Results(b, s, l, y, d)', globals(), locals())
