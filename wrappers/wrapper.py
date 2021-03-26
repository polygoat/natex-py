import pydash as _

class ParsedSentence(list): 
	pass

class ParsedToken: 
	def __repr__(self):
		return repr(self.__dict__)

class Wrapper:
	SUPPORTED_KEYS = ['literal', 'lemma', 'upos', 'xpos', 'udep', 'ner', 'span', 'features']
	SPLIT_FEATURES = True

	needs_setup = False

	def __init__(self, config):
		self.config = config

	@staticmethod
	def __split_features(feature_string):
		if feature_string:
			obj = dict()
			for features in feature_string.split('|'):
				key, value = features.split('=')
				obj[key.strip()] = value.strip()
			return obj

	def __parse_features(self, feature_string):
		if self.SPLIT_FEATURES:
			if isinstance(feature_string, str):
				if '=' in feature_string:
					return Wrapper.__split_features(feature_string)
		return feature_string

	def load_processor(self): pass

	def get_sentence(self, parsed): 
		return parsed
	
	def get_tokens(self, parsed_sentence):
		return parsed_sentence

	def preprocess(self, value, key):
		if isinstance(value, dict):
			for item, entry in value.items():
				value[item] = self.preprocess(entry, item)
			return value
		elif isinstance(value, list):
			return list(map(lambda item: self.preprocess(item, key), value))

		if key not in ['literal', 'lemma']:
			if value.isnumeric():
				return float(value)
			return str(value).upper()	
		return value

	def process(self, sentence, language_code='en'):
		if hasattr(self, 'load_processor'):
			nlp = self.load_processor()
			sentence = nlp(sentence)

	def map(self, item):
		index, token = item
		parsed_token = ParsedToken()
		for key in self.SUPPORTED_KEYS:
			props = _.get(self.KEY_MAPPING, key, key)

			if not isinstance(props, list):
				props = [props]

			values = []

			for prop in props:
				if '.' in prop:
					container_prop = prop.split('.')[0]
					container_value = _.get(token, container_prop, '')
					container_value = self.__parse_features(container_value)
					_.set_(token, container_prop, container_value)

				value = _.get(token, prop, '')
				value = self.__parse_features(value)
				value = self.preprocess(value, key)
				values.append(value)

			if len(values) == 1:
				values = values[0]

			_.set_(parsed_token, key, values)
		parsed_token.index = index
		return parsed_token

	def parse(self, sentence, language_code='en'):
		processor = self.load_processor(language_code)

		if self.needs_setup:
			return False
		
		parsed = processor(sentence)
		parsed_sentence = self.get_sentence(parsed)
		tokens = self.get_tokens(parsed_sentence)
		parsed_tokens = map(self.map, enumerate(tokens))
		parsed_tokens = ParsedSentence(parsed_tokens)
		parsed_tokens.literal = sentence
		return parsed_tokens

	def setup(self):
		print(f'No setup needed for {self.name}.')