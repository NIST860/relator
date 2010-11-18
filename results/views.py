from decimal import Decimal
from itertools import chain
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.http import Http404
from django.template import RequestContext
from relator.units import Quantity
from relator.data.models import EnergyPlusData
from relator.assemblies.models import Fuel
from relator.locations.models import State, Location, County
from relator.structures.models import Building
from relator.standards.models import Standard
from relator.zones.models import CensusRegion, CensusZone
from forms import VariableForm

def render(request, name, context=None):
	return render_to_response(name, RequestContext(request, context or {}))


def narrow(request):
	return render(request, 'narrow.html')


def by_state(request):
	if request.method == 'POST':
		states = State.objects.filter(pk__in=request.POST.getlist('code'))
		query = '&'.join('code=%s' % state.pk for state in states)
		return redirect('%s?%s' % (reverse(locations), query))
	return render(request, 'by-state.html', {
		'states': State.objects.all(),
	})


def by_region(request):
	if request.method == 'POST':
		zones = CensusZone.objects.filter(pk__in=request.POST.getlist('zone'))
		states = State.objects.filter(census_zone__in=zones)
		query = '&'.join('code=%s' % state.pk for state in states)
		return redirect('%s?%s' % (reverse(locations), query))
	return render(request, 'by-region.html', {'regions': CensusRegion.objects.all()})


def by_standard(request):
	if request.method == 'POST':
		standards = Standard.objects.filter(pk__in=request.POST.getlist('standard'))
		q = Q(_standard__in=standards)
		q |= Q(_standard=None, county___standard__in=standards)
		q |= Q(_standard=None, county___standard=None, state__standard__in=standards)
		if 'older' in request.POST:
			q |= Q(_standard=None, county___standard=None, state__standard=None)
		cities = Location.objects.filter(q)
		query = '&'.join('city=%s' % city.pk for city in cities)
		return redirect('%s?%s' % (reverse(locations), query))
	return render(request, 'by-standard.html', {'standards': Standard.objects.all()})


def locations(request):
	if request.method == 'POST':
		cities = Location.objects.filter(pk__in=request.POST.getlist('city'))
		query = '&'.join('city=%s' % city.pk for city in cities)
		return redirect('%s?%s' % (reverse(settings), query))
	states = State.objects.filter(pk__in=request.GET.getlist('code'))
	counties = County.objects.filter(pk__in=request.GET.getlist('county'))
	q = Q(state__in=states) | Q(county__in=counties) | Q(pk__in=request.GET.getlist('city'))
	cities = Location.objects.filter(q).distinct() or Location.objects.all()
	return render(request, 'locations.html', {'cities': cities})


def settings(request):
	cities = Location.objects.filter(pk__in=request.GET.getlist('city'))
	return render(request, 'settings.html', {
		'cities': cities,
		'buildings': Building.objects.all(),
		'standards': Standard.objects.all(),
		'years': list(range(1, 40+1)),
		'variables': VariableForm({'deflator': '0.03'}),
	})


def results(request):
	from relator.results.comparison import Comparison
	def data():
		for building in buildings:
			for location in locations:
				for year in (Quantity(length, 'years') for length in years):
					yield Comparison(standards, building, location, year, **variables)
	buildings = Building.objects.filter(pk__in=request.GET.getlist('building'))
	locations = Location.objects.filter(pk__in=request.GET.getlist('location'))
	standards = Standard.objects.filter(pk__in=request.GET.getlist('standard'))
	varform = VariableForm(request.GET)
	if not varform.is_valid():
		raise Http404
	variables = varform.variables()
	years = map(int, request.GET.getlist('year'))
	return render(request, 'results.html', {'data': data()})


def comparison(request):
	from relator.results.comparison import Comparison
	standards = Standard.objects.filter(pk__in=request.GET.getlist('standard'))
	building = Building.objects.get(pk=request.GET.get('building'))
	location = Location.objects.get(pk=request.GET.get('location'))
	deflator = request.GET.get('deflator')
	marr = request.GET.get('marr', None)
	year = int(request.GET.get('year'))
	comparison = Comparison(standards, building, location, year, deflator, marr)
	return render(request, 'comparison.html', {'comparison': comparison})
