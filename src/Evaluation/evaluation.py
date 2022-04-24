import csv
from typing import Callable, Dict, Iterable, Set

def lower_transform(predictions: Iterable[str]) -> Set[str]:
	return {pred.lower() for pred in predictions}

def csoc_transform_predictions(predictions: Iterable[str], transform_dict: Dict[str, str]) -> Set[str]:
	ret = set()
	print('original: ', predictions)
	for prediction in predictions:
		pred = prediction.lower()
		if pred in transform_dict:
			ret.add(transform_dict[pred])
		else:
			ret.add(pred)
	print('mapped: ', ret)
	return ret

class Evaluator:

	def __init__(self, input_path: str, categories: Iterable[str] = None, transformer: Callable[[Iterable[str]], Set[str]] = lower_transform, prediction_fieldname: str = 'Predictions'):
		self.inputfile = input_path
		self.transformer = transformer
		self.categories = set([cat.lower() for cat in categories]) if categories is not None else {'natural language processing', 'general', 'sequential', 'computer vision', 'reinforcement learning', 'graphs', 'audio'}
		self.stat_fields = ['tp', 'tn', 'fp', 'fn', 'support']
		self.resetStats()
		self.prediction_fieldnames = prediction_fieldname

	def resetStats(self):
		self.stats = {
						'overall' : {key: 0 for key in self.stat_fields},
						'overall_presentonly' : {key: 0 for key in self.stat_fields},
					}
		for category in self.categories:
			self.stats[category] = {key: 0 for key in self.stat_fields}

	def evaluate(self) -> Dict[str, str]:
		with open(self.inputfile) as f:
			self.reader = csv.DictReader(f, delimiter=';')
			for row in self.reader:
				self.stats['overall']['support'] += 1
				predictions = self.transformer(row[self.prediction_fieldnames].split(','))
				labels = [cat.lower() for cat in row['Labels'].split(',')]
				for category in self.categories:
					self.stats[category]['support'] += 1
					if category in predictions:
						if category in labels:
							self.stats['overall']['tp'] += 1
							self.stats[category]['tp'] += 1
						else:
							self.stats['overall']['fp'] += 1
							self.stats[category]['fp'] += 1
					else:
						if category in labels:
							self.stats['overall']['fn'] += 1
							self.stats[category]['fn'] += 1
						else:
							self.stats['overall']['tn'] += 1
							self.stats[category]['tn'] += 1

		for category in self.categories:
			if self.stats[category]['tp'] != 0 or self.stats[category]['fp'] != 0:
				for key in self.stat_fields:
					self.stats['overall_presentonly'][key] += self.stats[category][key]
				self.stats['overall_presentonly']['support'] += self.stats['overall']['support']

		for key, val in self.stats.items():
			self.stats[key]['precision'] = f"{val['tp']/(1 + val['tp'] + val['fp']):.2f}"
			self.stats[key]['recall'] = f"{val['tp']/(1 + val['tp'] + val['fn']):.2f}"
			self.stats[key]['sample_num'] = val['tp'] + val['fn']

		return self.stats.copy()
		
if __name__ == '__main__':
	pass