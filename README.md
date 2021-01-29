# Natural Language Expressions for Python
**NatEx**: Regular Expressions turbo-charged with notations for part-of-speech and dependency tree tags

## In a Nutshell
```python
import natex

utterance = natex('Sloths eat steak in New York')

# check if string begins with noun:
utterance.match(r'@NOUN')
# returns <natex.Match object; span=(0, 6), match='Sloths'>

# find first occurence of an adposition followed by a proper noun
utterance.search(r'@ADP <@PROPN>')  	
# returns <natex.Match object; span=(17, 28), match='in New York'>

# find first occurence of character sequence "ea"
utterance.search(r'ea')
# returns <natex.Match object; span=(7, 9), match='ea'>

# find first occurence of character sequence "ea" in nouns only
utterance.search(r'ea@NOUN')			
# returns <natex.Match object; span=(11, 16), match='steak'>

# find all occurences of nouns or proper nouns
utterance.findall(r'@(NOUN|PROPN)') 	
# returns ['Sloths', 'steak', 'New York']

# find all occurences of nouns or proper nouns starting with a lowercase s
utterance.findall(r's[^@]+@(NOUN|PROPN)') 
# returns ['steak']

# find all occurences of nouns or proper nouns starting with an s (irregardless of casing)
utterance.findall(r's[^@]+@(NOUN|PROPN)', natex.I)
# returns ['Sloths', 'steak']

```

## Goals & Design
The goal of NatEx is quick and simple parsing of tokens using their literal representation, part-of-speech, and dependency tree tags.
Think of it as an extension of [regular expressions] for natural language processing. The generated part-of-speech and dependency tree tags are provided by [stanza] and merged into a string that can be searched through.

[regular expressions]: https://docs.python.org/3/library/re.html
[stanza]: https://stanfordnlp.github.io/stanza

NatEx was designed primarily with simplicity in mind. 

## Examples
You can use it for simple response template generation (NLG):

```python
import natex

utterance = natex('Eat my shorts', 'en')

# look for token with imperative form
is_command = utterance.match(r'<!>')

if is_command:
	action_verb = utterance.search(r'<@VERB!>').lower()
	action_recipient = utterance.search(r'<#OBJ>')
	response = f'I will do my best to {action_verb} {action_recipient}!'
	
	# will contain 'I will do my best to eat shorts!'

```

## Installation

```bash
pip install natex
```

## Usage
NatEx provides the same API as the [`re` package], but adds the following special characters:

| Symbol | Meaning                  |
|:------:| ------------------------ |
| <      | token boundary (opening) | 
| :      | either @ or #  			| 
| @      | part of speech tag       | 
| #      | dependency tree tag      | 
| !      | imperative (mood)        | 
| >      | token boundary (closing) | 

[`re` package]: https://docs.python.org/3/library/re.html

### Configuration
You can set the **processing language** of NatEx using the second parameter `language_code`. 
It accepts a two-letter language-code, supporting [all languages officially supported by stanza].

[all languages officially supported by stanza]: https://stanfordnlp.github.io/stanza/available_models.html

```python

utterance = natex('Das Faultier isst keinen Gurkensalat', 'de')

```

### Methods

## Testing
You can use pytest in your terminal (simply type in `pytest`) to run the unit tests shipped with this package.
Install it by running `pip install pytest` in your terminal.