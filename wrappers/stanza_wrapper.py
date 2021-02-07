import os
import stanza
import contextlib
from .wrapper import Wrapper, ParsedSentence

class StanzaWrapper(Wrapper):	
	name = 'stanza'

	KEY_MAPPING = {
		'literal': 'text',
		'udep':'deprel',
		'features': 'feats',
		'span': 'misc'
	}
	SPLIT_FEATURES = True
	STANZA_PROCESSORS='tokenize,pos,ner,lemma,depparse'

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
					nlp = stanza.Pipeline(language_code, processors=self.STANZA_PROCESSORS, verbose=False)
				except FileNotFoundError:
					self.needs_setup = True
		
		if self.needs_setup:
			print('Download of stanza models necessary. You will have to re-run the script once the downloads are through.')

		return nlp

	def setup(self, language_code='en'):
		stanza.download(language_code, processors=self.STANZA_PROCESSORS, verbose=verbose)