from base import CostList
from mrr import Components
from insulation import InsulationCost
from windows import WindowCost
from lighting import LightingCost

class ComponentCostList(Components):
	children = {
		'insulation': InsulationCost,
		'windows': WindowCost,
		'lighting': LightingCost,
	}
