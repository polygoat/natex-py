#check out https://spacy.io/usage/models#languages

import spacy
from .wrapper import Wrapper

class SpacyWrapper(Wrapper):	
	__LANGUAGE_MODEL_MAPPING = {
		'da': 'da_core_news_{size}',
		'de': 'de_core_news_{size}',
		'el': 'el_core_news_{size}',
		'en': 'en_core_web_{size}',
		'es': 'es_core_news_{size}',
		'fr': 'fr_core_news_{size}',
		'it': 'it_core_news_{size}',
		'ja': 'ja_core_news_{size}',
		'lt': 'lt_core_news_{size}',
		'mk': 'mk_core_news_{size}',
		'nb': 'nb_core_news_{size}',
		'nl': 'nl_core_news_{size}',
		'pl': 'pl_core_news_{size}',
		'pt': 'pt_core_news_{size}',
		'ro': 'ro_core_news_{size}',
		'ru': 'ru_core_news_{size}',
		'xx': 'xx_ent_wiki_sm',
		'zh': 'zh_core_web_{size}',
	}

	KEY_MAPPING = {
		'literal': 'text',
		'lemma':'lemma_',
		'upos':'pos_', 
		'xpos':'tag_', 
		'udep':'dep_',
		'features': 'morph'
	}

	def __get_model_for(self, language_code, size):
		mapping = SpacyWrapper.__LANGUAGE_MODEL_MAPPING
		
		if language_code not in mapping:
			language_code = 'en'

		if language_code in mapping:
			model = mapping[language_code]
			model = model.format(size=size)
			return model
		else:
			raise RuntimeError('The required language model is not yet supported.')

	def load_processor(self, language_code='en', size='sm'):
		model = self.__get_model_for('en', size)
		if not model:
			self.needs_setup = True
			return False
		
		return spacy.load(model)