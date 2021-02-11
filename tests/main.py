#!/usr/bin/env python3

import os
import sys

sys.path.append(os.getcwd())

from natex import natex

PASSED = '\033[92m'
FAILED = '\033[31m'
RESET = '\033[0m'

def run_test(method, index, total):
	test_name = ' '.join(method.__name__.split('_')[1:])
	if method.__doc__:
		print(f'Testing {method.__doc__} ({index}/{total}) ...')
	else:
		print(f'Testing {test_name} ({index}/{total}) ...')
	method()
	print(f'{PASSED}Test #{index} passed.{RESET}')

def run_tests(*tests):
	total = len(tests)
	failed = 0

	for index, test in enumerate(tests):
		try:
			run_test(test, index + 1, total)
		except:
			print(f'{FAILED}Test #{index + 1} failed:\n ······> {sys.exc_info()[1]}{RESET}')
			failed += 1

	if failed:
		print(f'{PASSED}{total-failed} passed{RESET}. {FAILED}{failed} failed{RESET}.')
		exit(0)
	else:
		print(f'{PASSED}All {total} test(s) passed.{RESET}')
		exit(1)

def test_natex_en():
	"""English natex calls"""
	sentence = natex('Turn off the lights', 'en')
	
	result = sentence.findall('<>')
	assert result == ['Turn', 'off', 'the', 'lights'] 

	result = sentence.findall(r'<!>')
	assert result == ['Turn', 'off', 'the', 'lights'] 

	result = sentence.findall(r'<@NOUN>')
	assert result == ['lights'] 

	result = sentence.findall(r'<lights@NOUN>')
	assert result == ['lights'] 

	result = sentence.findall(r'<#SUBJ@NOUN>')
	assert result == [] 

	result = sentence.findall(r'<:OBJ>')
	assert result == ['lights'] 

	result = sentence.findall(r'lights@NOUN <>')
	assert result == [] 

	result = sentence.findall(r'@ADV#SUBJ')
	assert result == [] 

	result = sentence.findall(r'\<test\>')
	assert result == [] 

	result = sentence.findall(r'<(@NOUN|#AMOD)>')
	assert result == ['lights'] 

	result = sentence.findall(r'<(Affe|@NOUN|#AMOD)>')
	assert result == ['lights'] 


def test_natex_de():
	"""German natex calls"""
	sentence = natex('In New York frisst ein Hund aus der Hand.', 'de')

	result = sentence.match(r'@ADP <@PROPN>')
	assert str(result) == "<natex.Match object; span=(0, 11), match='In New York'>"

	result = sentence.match(r'@PROPN')
	assert result is None

	sentence = natex('In New York frisst ein Hund aus der hundsgemeinen Hand.', 'de')
	result = sentence.search(r'<@DET> <hund\w*@NOUN>', natex.I)
	assert str(result) == "<natex.Match object; span=(19, 27), match='ein Hund'>"

	sentence = natex('Ein Hund isst keinen Gurkensalat in New York.', 'de')

	result = sentence.findall(r'<G\w+@NOUN')
	assert result == ['Gurkensalat']

	result = sentence.search(r'@NOUN')
	assert str(result) == "<natex.Match object; span=(4, 8), match='Hund'>"

	result = sentence.sub(r'@(NOUN|PROPN)', 'Affe')
	assert result == 'Ein Affe isst keinen Affe in Affe.'

	result = sentence.sub(r'#NSUBJ', 'Affe')
	assert result == 'Ein Affe isst keinen Gurkensalat in New York.'

run_tests(test_natex_en, test_natex_de)