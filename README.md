# german_lookup
This is just a short python program to make looking up german words online easier. The original code was working with Ubuntu

# How to use it

There is an example in the how_to_use.py file. Let's go through it:

```python

import driver

if __name__ == "__main__":

    chromedriver_path = '/home/ignacio/Code/chromedriver'

    finder = driver.VocabFinder.chrome_driver(chrome_driver_path=chromedriver_path)

    # Relative paths as well?
    finder.lookup_txt_file(input_file_path='/home/ignacio/Code/ger_looker_upper/PyNouns.txt',
                           default_attributes=['gender'])
```

There are only 3 steps:
1. Select a webdriver
2. Initialize the VocabFinder class
3. Give it the text file to search for

### 1 Selecting a webdriver
I'm using the google chromedriver, which you can download from:
https://sites.google.com/a/chromium.org/chromedriver/downloads

### 2. Initialize the VocabFinder class
The `VocabFinder` class needs to have a webdriver. If you are also using the chromedriver you can just pass its path to the `chrome_driver()` class method.

If you want to use a different browser you can just call the `__init__()`method directly and pass an instance of your webdriver to the `webdriver` argument

### 3. Give it the text file to search for
The `VocabFinder` class uses the `lookup_txt_file()` method to get the words to look up online. In order to do that, it assumes that the
file at the `input_file_path` contains one word to look up per line.

At this point the user can also specify the output file name using the `output_file_path` argument. If it is empty, the output file 
will be in the same directory as the input file. The user can choose between having a CSV (Comma Separated Value) or a TSV (Tab Separated Value) output file by setting the `csv`
input boolean; `csv=True` will make it CSV, and `csv=False` will make it TSV. The default is TSV

MAKE SURE THE INPUT FILE IS SAVED IN UTF8 FORMAT

The `lookup_txt_file()` method will try to find the attributes specified in the `default_attributes` input argument
for all of the words in the input file. These default attributes are basically anything from the leo dictionary result page for a word.
The values should be specified in a list and they will be written to the output file in the order they are specified here.

The next sections go through the possible attributes. If any attribute is not found it will be left empty.

#### For any german word (eg. springen)
* `word_type`: specifies if the word can be a `noun`, `verb`, `adjadv` etc. (`['noun', 'verb']`)

#### For german nouns (eg. Haus)
* `gender`: the noun's gender (das)
* `plural`: the noun's plural (die Häuser)
* `noun_def`: the noun's definition (combines the first `VocabFinder.num_results` results [by default 3] from leo dict)

#### For german verbs (eg. Tanzen)
* `inf`: the verb's infinitive (Tanzen)
* `PII`: the verb's Partizip II (getanzt)
* `verb_def`: the verb's definition (combines the first `VocabFinder.num_results` results [by default 3] from leo dict)
#TODO, will be expanded in the future

