#!/usr/bin/env python3

import re
import os
import sys
import stanza
import argparse
import pydash as _
import contextlib
from dataclasses import dataclass

STANZA_PROCESSORS = 'tokenize,pos,ner,lemma,depparse'

@dataclass
class Data:
	def __init__(self, **kwargs):
		for kw, arg in kwargs.items():
			setattr(self, kw, arg)

	def __repr__(self):
		return repr(self.__dict__)

class NatExToken(Data):	pass
class NatEx(Data):	pass
class NatExSeparator(Data):	pass

class NatExMatch(Data):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.match = self.original[slice(*self._span)]

	def __repr__(self):
		return f'<natex.Match object; span={self.span()}, match=\'{self.match}\'>'

	def span(self):
		return tuple(self._span)

class NatEx:
	UNIVERSAL_POS_TAGS = ['SCONJ', 'PUNCT', 'PROPN', 'CCONJ', 'VERB', 'PRON', 'PART', 'NOUN', 'INTJ', 'SYM', 'NUM', 'DET', 'AUX', 'ADV', 'ADP', 'ADJ', 'X']
	UNIVERSAL_DEP_TAGS = ['REPARANDUM', 'DISLOCATED', 'PARATAXIS', 'DISCOURSE', 'VOCATIVE', 'GOESWITH', 'COMPOUND', 'ORPHAN', 'NUMMOD', 'ADVMOD', 'XCOMP', 'PUNCT', 'NSUBJ', 'FIXED', 'CSUBJ', 'CCOMP', 'APPOS', 'ADVCL', 'ROOT', 'NMOD', 'MARK', 'LIST', 'IOBJ', 'FLAT', 'EXPL', 'CONJ', 'CASE', 'AMOD', 'OBL', 'OBJ', 'DET', 'DEP', 'COP', 'CLF', 'AUX', 'ACL', 'CC']

	UNIVERSAL_POS_TAGS_RE = '|'.join(UNIVERSAL_POS_TAGS)
	UNIVERSAL_DEP_TAGS_RE = '|'.join(UNIVERSAL_DEP_TAGS)

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

		tokens = list(parsed_sentence.tokens)

		while(len(tokens)):
			token = tokens.pop(0).to_dict()[0]
			token_length = len(token['text'])
			parsed_separator = ''
			separator_len = 0

			if parsed_sentence.text[sentence_pos : sentence_pos + token_length] != token['text']:
				separator_len = parsed_sentence.text[sentence_pos:].index(token['text'])
				span = [sentence_pos, sentence_pos + separator_len]

				parsed_separator = NatExSeparator(index=index,
					literal=parsed_sentence.text[slice(*span)],
					span=span,
					is_token=False,
					is_separator=True
				)

				sentence_pos += separator_len

				self.separators.append(parsed_separator)
				representation += parsed_separator.literal
				index += 1

				for i in range(mapping_index, len(representation)):
					self.mapping[i] = span

				mapping_index = len(representation)

			span = self.__split_span(token['misc'])

			# merge multi-word named entities to one token
			if token['ner'][:2] == 'B-':
				while(True):
					next_token = tokens.pop(0)
					if parsed_separator:
						token['text'] += parsed_separator.literal
						span[1] += separator_len
						self.separators.pop()

					token['text'] += next_token.text
					token_length = len(token['text'])

					if next_token.ner[:2] == 'E-':
						break

			span[1] = span[0] + token_length

			parsed_token = NatExToken(index=index,
				literal=token['text'],
				lemma=_.get(token, 'lemma', ''),
				upos=_.get(token, 'upos', ''), 
				xpos=_.get(token, 'xpos'), 
				udep=_.get(token, 'deprel', '').upper(),
				span=span,
				features=self.__split_features(_.get(token, 'feats', '')),
				is_token=True,
				is_separator=False
			)
			sentence_pos += token_length

			self.tokens.append(parsed_token)

			optionals = ''

			if parsed_token.features:
				if 'mood' in parsed_token.features:
					optionals = '~' + parsed_token.features['mood'].upper()

			deps = parsed_token.udep.replace(':', ' ')
			natex_token = f'<{parsed_token.literal}@{parsed_token.upos}#{deps}{optionals}>'

			representation += natex_token

			for i in range(mapping_index, len(representation)):
				self.mapping[i] = span

			mapping_index = len(representation)

			index += 1

		self.original = self.parsed_sentence.text
		self.representation = representation

	def __repr__(self):
		return repr(self.__dict__)
		return str(self.representation)

	def __split_span(self, feature_string):
		data = self.__split_features(feature_string)
		span = data.values()
		span = list(map(int, span))
		return span

	def __split_features(self, feature_string):
		if feature_string:
			obj = dict()
			for features in feature_string.split('|'):
				key, value = features.split('=')
				obj[key.lower()] = value
			return obj

	def __natex_to_regex(self, pattern):
		pattern = re.sub(r'<@', r'<[^@]+@', pattern)
		pattern = re.sub(r'(^|\s)@', r'\1<[^@]+@', pattern)
		pattern = re.sub(r'@([^#\s]+)([^#A-Z]|$)', r'@\1#[^>]*>\2', pattern)
		pattern = re.sub(r'^([^<\s])', r'<\1', pattern)
		pattern = pattern.replace('>#', '#').replace('<#', '<[^#]+#')
		return pattern

	def __natex_to_str(self, natex_string):
		return re.sub(r'<|@[^#]+|#[^>]+>', '', natex_string).replace('<', '').replace('>', '')

	def __match_to_natex(self, match):
		if match:
			span = match.span()
			span = [self.mapping[span[0]][0], self.mapping[span[1]][0]]
			result = NatExMatch(_span=span, original=self.original)
			return result

	@staticmethod
	def setup(language_code='en', verbose=True):
		stanza.download(language_code, processors=STANZA_PROCESSORS, verbose=verbose)

	def match(self, pattern, flags=0):
		pattern = self.__natex_to_regex(pattern)
		print('PATTERN', pattern)
		print('REPRESENTATION', self.representation)
		re_match = re.match(pattern, self.representation, flags)
		return self.__match_to_natex(re_match)
			
	def search(self, pattern, flags=0):
		pattern = self.__natex_to_regex(pattern)
		re_match = re.search(pattern, self.representation, flags)
		return self.__match_to_natex(re_match)

	def findall(self, pattern, flags=0):
		pattern = self.__natex_to_regex(pattern)
		re_results = re.findall(pattern, self.representation, flags)
		results = list(map(self.__natex_to_str, re_results))
		return results

	def sub(self, pattern, by, flags=0):
		pattern = self.__natex_to_regex(pattern)
		result = re.sub(pattern, by, self.representation, flags)
		result = self.__natex_to_str(result)
		return result


def natex(sentence, language_code='en'):
	if isinstance(sentence, list):
		parsed_sentence = sentence
	else:
		needs_setup = False
		with open(os.devnull, 'w') as devnull:
			with contextlib.redirect_stderr(devnull):
				try:
					nlp = stanza.Pipeline(language_code, processors=STANZA_PROCESSORS, verbose=False)
					parsed = nlp(sentence)
				except FileNotFoundError:
					needs_setup = True
		
		if needs_setup:
			print('Download of stanza models necessary. This will only happen once.')
			NatEx.setup(language_code)
			return natex(sentence, language_code)

		parsed_sentence = parsed.sentences[0]
	
	result = NatEx(parsed_sentence)
	return result

natex.Match = NatExMatch
natex.I = re.I
natex.M = re.M
natex.S = re.S

natex.SYMBOL_ORDER = ['@','#','!']


# use splitting to convert from natex to regex:

def natex_to_regex(natex_string):
	BY_TOKENS = r'(?<=>)|(?=<)'
	#BY_ANY_SPACE = r'((?<=>)[^<]+(?=<)|[\s\n]|\\[stn ](?:[*+?]|\{[\d,\s]+\})?)+'

	natex_string = natex_string.replace(r'\<', '${ESCAPED_TOKEN_OPEN}')
	natex_string = natex_string.replace(r'\>', '${ESCAPED_TOKEN_CLOSE}')
	found_tokens = _.filter_(re.split(BY_TOKENS, natex_string))

	regex_tokens = []

	print(natex_string)

	for index, token in enumerate(found_tokens):
		used_symbols = set([])
		spacing = False
		found_tags = re.findall(r'(?<!\\)[#@:!][^#@:!>]*', token)

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
				tags[symbol] = tag[1:]
		
		print('USED_SYMBOLS', used_symbols)
		print('USED_TAGS', tags)

		if re.match(r'.*\s+$', token):
			token, spacing = re.split(r'(?=\s+$)', token)

		if not token.endswith('>'):
			token += '(?:[^>]|\\>)*>'

		if not token.startswith('<'):
			token = '<(?:[^<]|\\<)*' + token

		regex_tokens.append(token)

		if spacing:
			regex_tokens.append(spacing)

	print(regex_tokens)

	print('')


sentence = natex('Turn off the lights', 'en')

selector = '<>'
print(natex_to_regex(selector))

selector = r'<@NOUN>'
print(natex_to_regex(selector))

selector = r'<#SUBJ@NOUN>'
print(natex_to_regex(selector))

selector = r'<:amod>'
print(natex_to_regex(selector))

selector = r'<:amod'
print(natex_to_regex(selector))

selector = r'lights@NOUN <>'
print(natex_to_regex(selector))

selector = r'@ADV#SUBJ'
print(natex_to_regex(selector))

selector = r'\<test\>'
print(natex_to_regex(selector))

selector = r'New York'
print(natex_to_regex(selector))

selector = r'<dan\@gmail\.com>'
print(natex_to_regex(selector))

selector = r'<(@NOUN|#AMOD)>'
print(natex_to_regex(selector))


#print(sentence.match(r'~IMP'))