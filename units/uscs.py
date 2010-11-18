from quantities import BTU, h, kWh, UnitQuantity

MBH = UnitQuantity('mega_BTU_per_hour', (1000 * BTU) / h, 'MBH',
		aliases=['mega_BTUs_per_hour'])
cooling = UnitQuantity('cton', 12 * MBH, 'ton',
		aliases=['ctons',
		         'cooling_ton',
						 'cooling_tons',
						 'rton',
						 'rtons',
						 'refridgeration_ton',
						 'refridgeration_tons'])
gas = UnitQuantity('kft3', 3.413 * kWh, 'kft**3',
		aliases=['cubic_foot_gas',
		         'cubic_feet_gas'])
