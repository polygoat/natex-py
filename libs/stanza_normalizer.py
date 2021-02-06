import stanza
import pydash as _
from normalizer import Normalizer

class StanzaNormalizer(Normalizer):	
	KEY_MAPPING = {
		'literal': 'text',
		'udep':'deprel',
		'features': 'feats'
	}
	SPLIT_FEATURES = True

	def get_sentence(self, parsed):
		return parsed.sentences[0]

	def get_tokens(self, parsed_sentence):
		tokens = parsed_sentence.tokens
		tokens = _.map_(tokens, lambda token: token.to_dict()[0])
		return tokens

	def load_processor(self, language_code='en'):
		nlp = stanza.Pipeline(language_code, processors='tokenize,pos,ner,lemma,depparse', verbose=False)
		return nlp

norm = StanzaNormalizer()
sentence = norm.normalize('This is a test')
print(sentence)