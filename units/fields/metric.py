from relator.units.fields import UnitField
from django.db import models

SquareMeterField = UnitField('m**2')
UValueField = UnitField('W / (m**2 * K)')
WattField = UnitField('W')
GigaJouleField = UnitField('GJ')
JouleField = UnitField('J')
GramField = UnitField('g')
CostPerWattField = UnitField('dollar / W')
CostPerKiloWattHourField = UnitField('dollar / kWh')
KiloWattHourField = UnitField('kWh')
CostPerGramField = UnitField('dollar / g')
