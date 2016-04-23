# japanese-tools

japanese-tools is a set of misc tools for learning Japanese.


# lookup-and-format-in-memrise

This script looks up words in EDICT (JMdict) and save the words (including kanji, kana, and definition) in a format that can be used in [Memrise](http://www.memrise.com) to create modules.

Requirements:

* [mecab](https://github.com/SamuraiT/mecab-python3)
* [myougiden](https://pypi.python.org/pypi/myougiden)

    * Note that you probably will have to download the EDICT through myougiden the first time you use it (`sudo updatedb-myougiden -f`). See the README for myougiden for details.


The script works as below:

* It reads one line at a time in the input file, and will try to find one (and exactly one) definition for it.
* It prepares each entry by "reverse-conjugating" it. For example, if it sees 行った, it converts it to 行く first (because EDICT doesn't have 行った). Note that it would first try to find the reverse-conjugated form before the original one. There are some additional look-up logic, but this is the main one.
* Note that the look up is greedy---starting from the beginning of the entry, it will try to match an entry in EDICT that is as long as possible. This allows us to match longer entries such as idioms. For example, EDICT has an entry for 腹をくくる. The script will try to look up the meaning of the whole entry (and it will find it), instead of simply returning the definition of 腹.
* The script will then print out (and save in a file) the definitions in a format that Memrise can use. That is, the user can copy the output from here and paste it directly in Memrise to create a new module.


To use the output file in Memrise:

1. Go to memrise.com, create a new course or edit an existing course.
2. Click "Add Level" and then "Japanese".
3. Click "Advnaced" (on the right) and "Bulk add words".
4. Copy and the entire output file and paste into text field called "Paste your data here:"
5. Click Add.

Example input and output files have been included.

Known issues:

* Only the first definition is saved. This is by-design, as some words match lots of words in EDICT, and we do not want to save all the results in the output file. This is usually not a problem because the first result is usually the most commonly used one. However, this could cause problem once in a while, e.g., if you have くる in the input, it will find 繰る instead of the much more common 来る.






