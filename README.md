# **Nat**ural Language **Ex**pressions for Python
Regular Expressions turbo-charged with notations for part-of-speech and dependency tree tags

## In a Nutshell

## Goals & Design
The goal of NatEx is quick and simple parsing of tokens using their literal representation, part-of-speech, and dependency tree tags.
Think of it as an extension of regular expressions for natural language processing. The generated part-of-speech and dependency tree tags are provided by [stanza] and merged into a string that can be searched through.

```python
import natex

utterance = natex('Eat my shorts')

# look for token with imperative form
is_command = utterance.match(r'<!>')

if is_command:
	action_verb = utterance.search(r'<@VERB!>')
	response = f'I will try to {action_verb}!'

```

NatEx was designed primarily with simplicity in mind. 


## Installation

```bash
pip install natex
```

## Usage
NatEx provides the same API as the `re` package, but adds the following special characters:

| Symbol | Meaning                  |
|:------:| ------------------------ |
| <      | Token boundary (opening) | 
| :      | Any feature 	 	        | 
| @      | POS tag                  | 
| #      | dependency tree tag      | 
| !      | Imperative (mood)        | 
| >      | Token boundary (closing) | 


### Configuration
You can set the **processing language** of NatEx using the second parameter `language_code`. It accepts a two-letter language-code, supporting [all languages officially supported by stanza][https://stanfordnlp.github.io/stanza/available_models.html].

### Methods

## Testing
You can use pytest in your terminal (simply type in `pytest`) to run the unit tests shipped with this package.
Install it by running `pip install pytest` in your terminal.