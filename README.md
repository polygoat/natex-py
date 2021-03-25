# Natural Language Expressions for Python
**NatEx**: Regular Expressions turbo-charged with notations for part-of-speech and dependency tree tags

## In a Nutshell
```python
from natex import natex

sentence = natex('Sloths eat steak in New York')

# check if string begins with noun:
sentence.match(r'@NOUN')
# returns <natex.Match object; span=(0, 6), match='Sloths'>

# find first occurrence of an adposition followed by a proper noun
sentence.search(r'@ADP <@PROPN>')  	
# returns <natex.Match object; span=(17, 28), match='in New York'>

# find all occurrences of nouns or proper nouns
sentence.findall(r'@(NOUN|PROPN)') 	
# returns ['Sloths', 'steak', 'New York']

# find all occurrences of nouns or proper nouns starting with an s (irregardless of casing)
sentence.findall(r's[^@]+@(NOUN|PROPN)', natex.I)
# returns ['Sloths', 'steak']

```

## Goals & Design
The goal of NatEx is quick and simple parsing of tokens using their literal representation, part-of-speech, and dependency tree tags.
Think of it as an extension of [regular expressions] for natural language processing. The generated part-of-speech and dependency tree tags are provided by [stanza] and merged into a string that can be searched through.

[regular expressions]: https://docs.python.org/3/library/re.html
[stanza]: https://stanfordnlp.github.io/stanza

### Why not [Tregex], [Semgrex], or [Tsurgeon]?
NatEx was designed primarily with simplicity in mind.
Libraries like [Tregex], [Semgrex], or [Tsurgeon] may be able to match more complex patterns, but they have a steep learning curve and the patterns are hard to read. Plus NatEx is written for Python. It wraps the built-in `re` package with an abstraction layer and thus provides almost the same performance as any normal regex.

[Tregex]: https://nlp.stanford.edu/software/tregex/The_Wonderful_World_of_Tregex.ppt/
[Semgrex]: https://nlp.stanford.edu/nlp/javadoc/javanlp/edu/stanford/nlp/semgraph/semgrex/SemgrexPattern.html
[Tsurgeon]: https://nlp.stanford.edu/software/tregex/Tsurgeon2.ppt/

## Examples
You can use it for simple tagging (**NLU**):

```python
from natex import natex

sentence = natex('book flights from Munich to Chicago')
origin_location, destination_location = sentence.findall('<@PROPN>')
# origin_location ='Munich', destination_location = 'Chicago'

sentence = natex('I am being called Dan Borufka')
firstname, lastname = sentence.findall('<@PROPN>')
# firstname = 'Dan', lastname = 'Borufka'

sentence = natex('I need to go to Italy')
clause = sentence.search('<@ADP> <@PROPN>').match
# clause = 'to Italy'
destination = clause.split(' ')[1]

```

Or for simple response template generation (**NLG**):

```python
from natex import natex

sentence = natex('Eat my shorts')

# look for token with imperative form
is_command = sentence.match(r'<!>')

if is_command:
	action_verb = sentence.search(r'<@VERB!>').lower()
	action_recipient = sentence.search(r'<#OBJ>')
	response = f'I will do my best to {action_verb} {action_recipient}!'
	
	# will contain 'I will do my best to eat shorts!'

```

Even more (random) examples:

```python
from natex import natex

sentence = natex('Sloths eat steak in New York')

# find first occurrence of character sequence "ea" in nouns only
sentence.search(r'ea@NOUN')			
# returns <natex.Match object; span=(11, 16), match='steak'>

# find first occurrence of character sequence "ea"
sentence.search(r'ea')
# returns <natex.Match object; span=(7, 9), match='ea'>

# find all occurrences of nouns or proper nouns starting with a lowercase s
sentence.findall(r's[^@]+@(NOUN|PROPN)') 
# returns ['steak']

sentence = natex('Ein Hund isst keinen Gurkensalat in New York.', 'de')

# replace the nominal subject with the literal 'Affe'
sentence.sub(r'#NSUBJ', 'Affe')
# returns 'Ein Affe isst keinen Gurkensalat in New York.'
```

Check out [`test.py`] for some more examples!

[`test.py`]: https://github.com/polygoat/natex-py/blob/main/test.py

## Installation
Run:

```bash
pip install natex
```

By default, NatEx only installs the English models for stanza.
Use the following command to download a model for another language: 

```bash
python -m natex setup <language_code>`
```

e.g. for French use:

```bash
python -m natex setup fr`
```

Visit https://github.com/secretsauceai/natex-py for a full list of supported language codes.

## Usage
NatEx provides the same API as the [`re` package], but adds the following special characters:

[`re` package]: https://docs.python.org/3/library/re.html

| Symbol | Meaning                  | Example pattern | Meaning 					    |
|:------:| ------------------------ |:---------------:| ------------------------------- |
| <      | token boundary (opening) | <New            | _Find tokens starting with "New"_ |
| :      | either @ or #  			| <:ADV 		  | _Find tokens with e.g. universal POS "ADV" or dep. tree tag "ADVMOD"_ |
| @      | part of speech tag       | @ADJ 		  	  | _Find tokens that are adjectives_ |
| #      | dependency tree tag      | #OBJ 			  | _Find the objects of the sentence_ |
| !      | imperative (mood)        | <!>			  | _Find any verbs that are in imperative form_ |
| >      | token boundary (closing) | York>			  | _Find all tokens ending in "York"_ |

If you combine features (e.g. seeking by part of speech and dependency tree simultaneously) make sure you provide them in the order of the table above.

✔ This will work:
```python
natex('There goes a test sentence').findall(r'<@NOUN#OBJ>')
```

✘ But this won't:
```python
natex('There goes a test sentence').findall(r'<#OBJ@NOUN>')
```

Calling the `natex()` function returns a `NatEx` instance. See [API] for a more detailed description.
Just as the `re.Match` returning methods provided by Python's built-in `re` package, NatEx' equivalents will return a `natex.Match` object containing a `span` and a `match` property referring to position and substring of the sentence respectively.

You can use our wrapper architecture to use Natex with any existing library or e.g. POS tagger you want. We have already created a wrapper for [Stanza] and [Spacy] respectively. Here's how you use them:

[Stanza]: https://stanfordnlp.github.io/stanza/ 
[Spacy]: https://spacy.io/

```python
natex.use('stanza')
```

You might pass any [Stanza Pipeline] or [Spacy load options] as second parameter:

[Stanza]: https://stanfordnlp.github.io/stanza/pipeline.html#pipeline
[Spacy load options]: https://spacy.io/api/top-level

```python 
natex.use('stanza', use_gpu=False) # will use Stanza without CUDA
```

If you want to create wrappers for other or your own libraries please refer to the [Wrapping Other Libraries] section.

[Wrapping Other Libraries]: #Wrapping-Other-Libraries 

[API]: #api

### Configuration
You can set the **processing language** of NatEx using the second parameter `language_code` (defaults to 'en'). 
It accepts a two-letter language-code, supporting [all languages officially supported by stanza].

[all languages officially supported by stanza]: https://stanfordnlp.github.io/stanza/available_models.html

```python

sentence = natex('Das Faultier isst keinen Gurkensalat', 'de')

```

When you run NatEx for the first time, it will check for the existence of the corresponding language models and download them if necessary. All subsequent calls to `natex()` will exclude that step.

### API
The API is derived from Python's built-in `re` package:

**NatEx**

**.match(pattern, flags)**

Checks (from the beginning of the string) whether the sentence matches a _pattern_ and returns a `natex.Match` object or `None` otherwise.

**.search(pattern, flags)**
Returns a `natex.Match` object describing the first substring matching _pattern_.

**.findall(pattern, flags)**
Returns all found strings matching _pattern_ as a list.

**.split(pattern, flags)**
Splits the sentence by all occurrences of the found _pattern_ and returns a list of strings.

**.sub(pattern, replacement, flags)**
Replaces all occurrences of the found _pattern_ by _replacement_ and returns the changed string.

## Wrapping Other Libraries

You can wrap other libraries by forking this repository and creating a new wrapper in `wrappers`. Import and extend the **wrapper class** found in the same directory. The bare minimum structure for your file should look like this:

```python
from .wrapper import Wrapper
from .new_engine import NewEngine

class NewEngineWrapper(Wrapper):
	name = 'new_engine'

	KEY_MAPPING = {
		'upos': 'pos',
		...
	}

	def load_processor(self, language_code):
		return NewEngine.load_nlp_model(language_code)

```

You'll then be able to use it for natex like so:

```python
natex.use('new_engine')
```

## Testing
You can run [`tests/main.py`] in your terminal to run the basic unit tests shipped with this package.

[`tests/main.py`]: https://github.com/polygoat/natex-py/blob/main/tests/main.py