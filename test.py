from natex import natex

def test_nlpex_en():
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


def test_nlpex_de():
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
