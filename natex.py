#!/usr/bin/env python3

import re
import argparse
import importlib
import pydash as _
from types import ModuleType
from dataclasses import dataclass

@dataclass
class FromKw:
	def __init__(self, **kwargs):
		for arg, value in kwargs.items():
			setattr(self, arg, value)

class NatExToken(FromKw):	
	SYMBOL_ORDER = ['', '@','#', '!']

	def __repr__(self):
		return repr(self.__dict__)

	def is_empty(self, check_text=True):
		symbols = NatExToken.SYMBOL_ORDER

		if not check_text:
			symbols = symbols[1:]

		for symbol in symbols:
			value = getattr(self, symbol)
			if value:
				if value.strip() and value.strip() != '<>':
					return False

		if check_text:
			if ':' in self.literal:
				return False

		return True

	def render(self):
		output = ''

		if self.literal == '<>' or self.is_empty():
			output = '<[^>]+>'
		else:
			previous_symbols = ''

			for i, symbol in enumerate(NatExToken.SYMBOL_ORDER):
				value = getattr(self, symbol)
				if value:
					if value.startswith('<'):
						value = value[1:]
					output += symbol + value
				else:
					next_symbol = _.get(NatExToken.SYMBOL_ORDER, i + 1)
					
					if symbol != '!':
						if next_symbol != '!':
							output += symbol + '[^<' + previous_symbols + next_symbol + ']*'

				previous_symbols += symbol

			output += '[^>]*'

			any_selector = getattr(self, ':')

			if any_selector:
				if self.is_empty(check_text=False):
					output = f'([@#]?{any_selector})'
				else:
					output = f'([@#]?{any_selector}|{output})'

			if not self.literal.endswith('>'):
				output += r'(?:[^>]|\\>)*>'
			else:
				output += '>'

			if not self.literal.startswith('<'):
				output = r'<(?:[^<]|\\<)*' + output
			else:
				output = '<' + output

		return output

class NatExMatch(FromKw):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.match = self.original[slice(*self._span)]

	def __repr__(self):
		return f'<natex.Match object; span={self.span()}, match=\'{self.match}\'>'

	def span(self):
		return tuple(self._span)

class NatExSeparator(FromKw):
	@staticmethod
	def from_string(literal, index, span):
		return NatExSeparator(index=index,
			literal=literal[slice(*span)], 
			span=span, 
			is_token=False, 
			is_separator=True
		)

class NatEx:
	UNIVERSAL_POS_TAGS = ['SCONJ', 'PUNCT', 'PROPN', 'CCONJ', 'VERB', 'PRON', 'PART', 'NOUN', 'INTJ', 'SYM', 'NUM', 'DET', 'AUX', 'ADV', 'ADP', 'ADJ', 'X']
	UNIVERSAL_DEP_TAGS = ['REPARANDUM', 'DISLOCATED', 'PARATAXIS', 'DISCOURSE', 'VOCATIVE', 'GOESWITH', 'COMPOUND', 'ORPHAN', 'NUMMOD', 'ADVMOD', 'XCOMP', 'PUNCT', 'NSUBJ', 'FIXED', 'CSUBJ', 'CCOMP', 'APPOS', 'ADVCL', 'ROOT', 'NMOD', 'MARK', 'LIST', 'IOBJ', 'FLAT', 'EXPL', 'CONJ', 'CASE', 'AMOD', 'OBL', 'OBJ', 'DET', 'DEP', 'COP', 'CLF', 'AUX', 'ACL', 'CC']

	engine = None
	pipeline = ['tokenize', 'pos', 'ner', 'lemma', 'depparse']

	def __init__(self, parsed_sentence):
		self.parsed_sentence = parsed_sentence
		self.tokens = []
		self.separators = []
		self.representation = ''
		self.mapping = {}

		representation = ''
		sentence_pos = 0
		index = 0
		mapping_index = 0

		tokens = parsed_sentence

		while(len(tokens)):
			token = tokens.pop(0)
			token_length = len(token.literal)
			parsed_separator = ''
			separator_len = 0

			if parsed_sentence.literal[sentence_pos : sentence_pos + token_length] != token.literal:
				separator_len = parsed_sentence.literal[sentence_pos:].index(token.literal)
				span = [sentence_pos, sentence_pos + separator_len]

				parsed_separator = NatExSeparator.from_string(parsed_sentence.literal, index, span)
				sentence_pos += separator_len

				self.separators.append(parsed_separator)
				representation += parsed_separator.literal
				index += 1

				for i in range(mapping_index, len(representation) + 1):
					self.mapping[i] = span

				mapping_index = len(representation)

			# merge multi-word named entities to one token
			if token.ner[:2] == 'B-':
				while(True):
					next_token = tokens.pop(0)
					if parsed_separator:
						token.literal += parsed_separator.literal
						token.span[1] += separator_len
						self.separators.pop()

					token.literal += next_token.literal
					token_length = len(token.literal)

					if next_token.ner[:2] == 'E-':
						break

			token.span[1] = token.span[0] + token_length
			token.index = index

			parsed_token = NatExToken(**token.__dict__)
			sentence_pos += token_length

			self.tokens.append(parsed_token)

			optionals = self.__get_optionals(parsed_token)

			deps = parsed_token.udep.replace(':', ' ')
			natex_token = f'<{parsed_token.literal}@{parsed_token.upos}#{deps}{optionals}>'

			representation += natex_token

			for i in range(mapping_index, len(representation) + 1):
				self.mapping[i] = token.span

			mapping_index = len(representation)

			index += 1

		self.original = self.parsed_sentence.literal
		self.representation = representation

	def __repr__(self):
		return str(self.representation)#

	def __get_optionals(self, parsed_token):
		optionals = ''
		if parsed_token.features:
			if _.get(parsed_token.features, 'MOOD') == 'IMP':
				optionals = '!'
		return optionals

	def __to_regex(self, natex_string):
		TAGS_REGEX = r'(?<!\\)[#@:!][^#@:!>]*'
		
		parsed_natex = natex_string.replace(r'\\<', '${ESCAPED_TOKEN_OPEN}')
		parsed_natex = parsed_natex.replace(r'\\>', '${ESCAPED_TOKEN_CLOSE}')

		found_tokens = _.filter_(re.split(r'(?<=>)|(?=<)', parsed_natex))
		regex_tokens = []

		for index, token in enumerate(found_tokens):
			spacing = False

			if not re.match(r'\s+$', token):
				used_symbols = set([])
				found_tags = re.findall(TAGS_REGEX, token)
				cleaned_parts = re.split(TAGS_REGEX, token)
				cleaned_parts = [part for part in cleaned_parts if part not in ['', '<', '>']]

				tags = {
					'#': None,
					'@': None,
					':': None,
					'!': False
				}

				for tag in found_tags:
					symbol = tag[0]
					if symbol in '@#:!':
						used_symbols.add(symbol)
						tags[symbol] = tag[1:].strip().upper()
				
				tags[''] = ''.join(cleaned_parts)
				tags['literal'] = natex_string
				search_token = NatExToken(**tags)
				token = search_token.render()

				if re.match(r'.*\s+$', token):
					token, spacing = re.split(r'(?=\s+$)', token)

				if '[^<]*' not in token:
					token = token.replace('<(', '<[^<]*(')

			regex_tokens.append(token)

			if spacing:
				regex_tokens.append(spacing)

		output = ''.join(regex_tokens)
		output = output.replace('${ESCAPED_TOKEN_OPEN}', '<')
		output = output.replace('${ESCAPED_TOKEN_CLOSE}', '>')
		output = re.sub(r'\((?!\?:)', '(?:', output)
		output = output.replace('><', '> <')
		output = output.replace('<[^<]*(?:[^<]|\\<)*', '<(?:[^<]|\\<)*')

		self.last_regex = f'({output})'

		return self.last_regex

	def __to_str(self, natex_string):
		return re.sub(r'<|@[^#]+|#[^>]+>', '', natex_string).replace('<', '').replace('>', '')

	def __from_match(self, match, regex):
		if match:
			span = match.span()
			span = [self.mapping[span[0]][0], self.mapping[span[1]][0]]
			result = NatExMatch(_span=span, original=self.original, regex=regex)
			return result

	@staticmethod
	def setup(engine, language_code='en', verbose=True):
		NatEx.use(engine)
		NatEx.engine.setup(language_code)

	@staticmethod
	def use(engine, **config=False):
		if isinstance(engine, ModuleType):
			engine = engine.__name__

		#base = '' if __name__ == '__main__' else __name__.split('.')[0] + '.'
		base = ''
		wrapper_name = f'{_.upper_first(engine)}Wrapper'
		wrapper_module = importlib.import_module(f'{base}wrappers.{engine}_wrapper', base)
		wrapper_class = getattr(wrapper_module, wrapper_name)

		NatEx.engine = wrapper_class(config)
		NatEx.engine.PIPELINE = NatEx.pipeline

	def match(self, pattern, flags=0):
		pattern = self.__to_regex(pattern)
		re_match = re.match(pattern, self.representation, flags)
		return self.__from_match(re_match, pattern)
			
	def search(self, pattern, flags=0):
		pattern = self.__to_regex(pattern)
		re_match = re.search(pattern, self.representation, flags)
		return self.__from_match(re_match, pattern)

	def split(self, pattern, flags=0):
		pattern = self.__to_regex(pattern)
		results = re.split(pattern, self.representation, flags)
		results = list(map(results, self.__to_str))
		return results

	def findall(self, pattern, flags=0):
		pattern = self.__to_regex(pattern)
		re_results = re.findall(pattern, self.representation, flags)
		results = list(map(self.__to_str, re_results))
		return results

	def sub(self, pattern, by, flags=0):
		pattern = self.__to_regex(pattern)
		result = re.sub(pattern, by, self.representation, flags)
		result = self.__to_str(result)
		return result


def natex(sentence, language_code='en'):
	if isinstance(sentence, list):
		parsed_sentence = sentence
	else:
		parsed_sentence = NatEx.engine.parse(sentence, language_code)
		if NatEx.engine.needs_setup:
			raise Exception(f'Download of {NatEx.engine.name} models necessary. Please use `python -m natex setup stanza {language_code}` to do so. Note you will have to re-run the script once the downloads are through.')
			return None

	result = NatEx(parsed_sentence)
	return result

natex.Class = NatEx
natex.Match = NatExMatch
natex.Token = NatExToken
natex.use = NatEx.use
natex.I = re.I
natex.M = re.M
natex.S = re.S

natex.use('stanza')

if __name__ == '__main__':
	import argparse

	parser = argparse.ArgumentParser(description='Configure NatEx local installation using the `setup` sub-command')
	parser.add_argument('command', help='setup')
	parser.add_argument('params', metavar='N', nargs='*')
	args = parser.parse_args()

	if args.command == 'setup':
		NatEx.setup(*args.params)