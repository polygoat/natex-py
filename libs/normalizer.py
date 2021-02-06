import pydash as _

class Normalizer:
	SUPPORTED_KEYS = ['literal', 'lemma', 'upos', 'xpos', 'udep', 'features']
	SPLIT_FEATURES = True

	@staticmethod
	def __split_features(feature_string):
		if feature_string:
			obj = dict()
			for features in feature_string.split('|'):
				key, value = features.split('=')
				obj[key.strip()] = value.strip()
			return obj

	def load_processor(self): pass

	def get_sentence(self, parsed): 
		return parsed
	
	def get_tokens(self, parsed_sentence):
		return parsed_sentence

	def preprocess(self, tag, key):
		if key not in ['literal', 'lemma']:
			return str(tag).upper()	
		return tag

	def process(self, sentence, language_code='en'):
		if hasattr(self, 'load_processor'):
			nlp = self.load_processor()
			sentence = nlp(sentence)

	def map(self, item):
		index, token = item
		parsed_token = {}
		for key in Normalizer.SUPPORTED_KEYS:
			prop = _.get(self.KEY_MAPPING, key, key)
			value = _.get(token, prop, '')
			value = self.preprocess(value, key)

			if key == 'features':
				if self.SPLIT_FEATURES:
					value = Normalizer.__split_features(value)

			_.set_(parsed_token, key, value)
		parsed_token['index'] = index
		return parsed_token

	def normalize(self, sentence, language_code='en'):
		processor = self.load_processor(language_code)
		parsed = processor(sentence)
		parsed_sentence = self.get_sentence(parsed)
		tokens = self.get_tokens(parsed_sentence)
		parsed_tokens = _.map_(enumerate(tokens), self.map)
		return parsed_tokens