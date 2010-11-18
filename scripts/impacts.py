impacts = (
('Carbon Dioxide',2.558264009217000E+07,'2.900000000000000E-01', 'g'),
('Acidification',7.800200000000000E+09,'3.000000000000000E-02', 'g'),
('Eutrophication',1.921419564000000E+04,'6.000000000000000E-02', 'g'),
('Natural Resource Depletion',3.530900000000000E+04,'1.000000000000000E-01', 'kg'),
('Water Intake',5.299577548000000E+05,'8.000000000000000E-02', 'L'),
('Criteria Air Pollutants',1.920000000000000E+04,'9.000000000000000E-02', 'g'),
('Smog',1.515000317500000E+05,'4.000000000000000E-02', 'g'),
('Ecotoxicity',8.164672000000000E+04,'7.000000000000000E-02', 'g'),
('Ozone Depletion',3.401946800000000E+02,'2.000000000000000E-02', 'g'),
('Human Toxicity--Noncancer',1.650085717862100E+08,'5.000000000000000E-02', 'g'),
('Human Toxicity--Cancer',5.216618270000000E+03,'8.000000000000000E-02', 'g'),
)

from carbon.models import Impact
for (name, normalization, weight, unit) in impacts:
	Impact.objects.get_or_create(name=name, defaults={
		'normalization': normalization,
		'weight': weight,
		'unit': unit})
