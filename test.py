from natex import natex

def test_nlpex():
	result = natex('In New York frisst ein Hund aus der Hand.', 'de').match(r'@ADP <@PROPN>')
	assert str(result) == "<natex.Match object; span=(0, 11), match='In New York'>"

	result = natex('In New York frisst ein Hund aus der Hand.', 'de').match(r'@PROPN')
	assert result is None

	result = natex('In New York frisst ein Hund aus der hundsgemeinen Hand.', 'de').search(r'<@DET> <hund\w*@NOUN>', natex.I)
	assert str(result) == "<natex.Match object; span=(19, 27), match='ein Hund'>"

	result = natex('Der Hund isst keinen Gurkensalat in New York.', 'de').findall(r'G\w+@NOUN')
	assert result == ['Gurkensalat']

	result = natex('Ein Hund isst keinen Gurkensalat in New York.', 'de').search(r'@NOUN')
	assert str(result) == "<natex.Match object; span=(4, 8), match='Hund'>"

	result = natex('Ein Hund isst keinen Gurkensalat in New York.', 'de').sub(r'@(NOUN|PROPN)', 'Affe')
	assert result == 'Ein Affe isst keinen Affe in Affe.'

	result = natex('Ein Hund isst keinen Gurkensalat in New York.', 'de').sub(r'#NSUBJ', 'Affe')
	assert result == 'Ein Affe isst keinen Gurkensalat in New York.'


def __test_nlpex_en():
	sentence = natex('Turn off the lights', 'en')
	selector = '<>'
	print(selector, '\n', sentence.findall(selector), '\n', '-' * 40, '\n')

	selector = r'<!>'
	print(selector, '\n', sentence.findall(selector), '\n', '-' * 40, '\n')

	selector = r'<@NOUN>'
	print(selector, '\n', sentence.findall(selector), '\n', '-' * 40, '\n')

	selector = r'<lights@NOUN>'
	print(selector, '\n', sentence.findall(selector), '\n', '-' * 40, '\n')

	selector = r'<#SUBJ@NOUN>'
	print(selector, '\n', sentence.findall(selector), '\n', '-' * 40, '\n')

	selector = r'<:OBJ>'
	print(selector, '\n', sentence.findall(selector), '\n', '-' * 40, '\n')

	selector = r'lights@NOUN <>'
	print(selector, '\n', sentence.findall(selector), '\n', '-' * 40, '\n')

	selector = r'@ADV#SUBJ'
	print(selector, '\n', sentence.findall(selector), '\n', '-' * 40, '\n')

	selector = r'\<test\>'
	print(selector, '\n', sentence.findall(selector), '\n', '-' * 40, '\n')

	selector = r'New York'
	print(selector, '\n', sentence.findall(selector), '\n', '-' * 40, '\n')

	selector = r'<dan\@gmail\.com>'
	print(selector, '\n', sentence.findall(selector), '\n', '-' * 40, '\n')

	selector = r'<(@NOUN|#AMOD)>'
	print(selector, '\n', sentence.findall(selector), '\n', '-' * 40, '\n')

	selector = r'<(Affe|@NOUN|#AMOD)>'
	print(selector, '\n', sentence.findall(selector), '\n', '-' * 40, '\n')
