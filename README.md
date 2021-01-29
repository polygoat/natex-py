# Natural Language Expressions for Python
**NatEx**: Regular Expressions turbo-charged with notations for part-of-speech and dependency tree tags

## In a Nutshell
```python
from natex import natex

utterance = natex('Sloths eat steak in New York')

# check if string begins with noun:
utterance.match(r'@NOUN')
# returns <natex.Match object; span=(0, 6), match='Sloths'>

# find first occurence of an adposition followed by a proper noun
utterance.search(r'@ADP <@PROPN>')  	
# returns <natex.Match object; span=(17, 28), match='in New York'>

# find first occurence of character sequence "ea" in nouns only
utterance.search(r'ea@NOUN')			
# returns <natex.Match object; span=(11, 16), match='steak'>

# find all occurences of nouns or proper nouns
utterance.findall(r'@(NOUN|PROPN)') 	
# returns ['Sloths', 'steak', 'New York']

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
You can use it for simple tagging (**NLU**):

```python
from natex import natex

utterance = natex('book flights from Munich to Chicago')
start_location, destination_location = utterance.findall('@PROPN')
# start_location ='Munich', destination_location = 'Chicago'

utterance = natex('I am being called Dan Borufka')
firstname, lastname = utterance.findall('@PROPN')
# firstname = 'Dan', lastname = 'Borufka'

utterance = natex('I need to go to Italy')
clause = utterance.search('<@ADP> <@PROPN>').match
# clause = 'to Italy'
destination = clause.split(' ')[1]

```

Or for simple response template generation (**NLG**):

```python
from natex import natex

utterance = natex('Eat my shorts')

# look for token with imperative form
is_command = utterance.match(r'<!>')

if is_command:
	action_verb = utterance.search(r'<@VERB!>').lower()
	action_recipient = utterance.search(r'<#OBJ>')
	response = f'I will do my best to {action_verb} {action_recipient}!'
	
	# will contain 'I will do my best to eat shorts!'

```

Even more (random) examples:

```python
from natex import natex

utterance = natex('Sloths eat steak in New York')

# find first occurence of character sequence "ea"
utterance.search(r'ea')
# returns <natex.Match object; span=(7, 9), match='ea'>

# find all occurences of nouns or proper nouns starting with a lowercase s
utterance.findall(r's[^@]+@(NOUN|PROPN)') 
# returns ['steak']

natex('Ein Hund isst keinen Gurkensalat in New York.', 'de').sub(r'#NSUBJ', 'Affe')
# returns 'Ein Affe isst keinen Gurkensalat in New York.'
```


## Installation
Run:

```bash
pip install natex
```

## Usage
NatEx provides the same API as the [`re` package], but adds the following special characters:
[`re` package]: https://docs.python.org/3/library/re.html

| Symbol | Meaning                  |
|:------:| ------------------------ |
| <      | token boundary (opening) | 
| :      | either @ or #  			| 
| @      | part of speech tag       | 
| #      | dependency tree tag      | 
| !      | imperative (mood)        | 
| >      | token boundary (closing) | 

Calling the `natex()` function returns a `NatEx` instance. See [Methods] for a more detailed description.
Just as the `re.Match` returning methods provided by Python's built-in `re` package, NatEx' equivalents will return a `natex.Match` object containing a `span` and a `match` property referring to position and substring of the utterance respectively.

### Configuration
You can set the **processing language** of NatEx using the second parameter `language_code` (defaults to 'en'). 
It accepts a two-letter language-code, supporting [all languages officially supported by stanza].

[all languages officially supported by stanza]: https://stanfordnlp.github.io/stanza/available_models.html

```python

utterance = natex('Das Faultier isst keinen Gurkensalat', 'de')

```

When you run NatEx for the first time, it will check for the existence of the corresponding language models and download them if necessary. All subsequent calls to `natex()` will exclude that step.

### Methods
Methods are derived from Python's built-in `re` package:

**.match(pattern, flags)**
Checks (from the beginning of the string) whether the utterance matches a _pattern_ and returns a `natex.Match` object or `None` otherwise.

**.search(pattern, flags)**
Returns a `natex.Match` object describing the first substring matching _pattern_.

**.findall(pattern, flags)**
Returns all found strings matching _pattern_ as a list.

**.split(pattern, flags)**
Splits the utterance by all occurences of the found _pattern_ and returns a list of strings.

**.sub(pattern, replacement, flags)**
Replaces all occurences of the found _pattern_ by _replacement_ and returns the changed string.

## Testing
You can use pytest in your terminal (simply type in `pytest`) to run the unit tests shipped with this package.
Install it by running `pip install pytest` in your terminal.