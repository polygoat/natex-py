import os
import stanza
import contextlib
from .wrapper import Wrapper, ParsedSentence

class StanzaWrapper(Wrapper):	
	name = 'stanza'

	DEBUGGING = False
	SPLIT_FEATURES = True
	KEY_MAPPING = {
		'literal': 'text',
		'udep':'deprel',
		'features': 'feats',
		'span': ['misc.start_char', 'misc.end_char']
	}

	def __get_processors(self):
		return ','.join(self.PIPELINE)

	def get_sentence(self, parsed):
		return parsed.sentences[0]

	def get_tokens(self, parsed_sentence):
		tokens = parsed_sentence.tokens
		tokens = map(lambda token: token.to_dict()[0], tokens)
		return list(tokens)

	def load_processor(self, language_code='en'):
		nlp = False
		# suppress stanza warnings
		with open(os.devnull, 'w') as devnull:
			with contextlib.redirect_stderr(devnull):
				try:
					nlp = stanza.Pipeline(language_code, processors=self.__get_processors(), verbose=self.DEBUGGING, **self.config)
				except FileNotFoundError:
					self.needs_setup = True
		return nlp

	def setup(self, language_code='en'):
		stanza.download(language_code, processors=self.__get_processors(), verbose=self.DEBUGGING)