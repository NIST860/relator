from relator.units.fields import UnitField
from django.db import models

InchField = UnitField('in')
FootField = UnitField('ft')
SquareFootField = UnitField('ft**2')
UValueField = UnitField('BTU / (h * ft**2 * degF)')
MBHField = UnitField('MBH')
TonField = UnitField('refridgeration_ton')

CostPerMBHField = UnitField('dollar / MBH')
CostPerTonField = UnitField('dollar / refridgeration_ton')
CostPerSquareFootField = UnitField('dollar / ft**2')

BTUperYearField = UnitField('BTU / year')
