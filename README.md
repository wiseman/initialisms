# finalletters

Guesses sentences from initial letters of each word using the
unreasonable power of statistics.  E.g., given the input "obv" it will
output "o blessed virgin".

Inspired by http://norvig.com/ngrams/ch14.pdf and
http://ask.metafilter.com/255675/Decoding-cancer-addled-ramblings.


## Getting ready to use it

It's probably easiest to use virtualenv:

```
$ virtualenv env
```

Then install nltk and python-gflags:

```
$ env/bin/pip install nltk python-gflags
```


## Using it

Start the program.  It will take 10-20 seconds to load data:

```
$ env/bin/python decode.py bible-kjv.txt hymnprayerbo00kunz_djvu.txt prayerbookreligi00lasauoft_djvu.txt
```

Once it says "Enter initials:", you can type something like "obv" and
press Enter.  10-20 seconds later it will output something like this:

```
(7.810582510127791e-07, ['o', 'blessed', 'virgin'])
```

This means that its best guess for "obv" is "o blessed virgin", with a
probability of some small number.

This code is unoptimized and slow.  If you try to decode more than 3
or 4 characters, you're going to be waiting a long time.


### Corpora

The program makes its guesses based on text you feed it.  I've included three pieces of text:

1. [King James Bible](https://en.wikipedia.org/wiki/King_James_Version)
2. [Prayer-book for religious : a complete manual of prayers and devotions for the use of the members of all religious communities : a practical guide to the particular examen and to the methods of meditation (1914, c1904)](https://archive.org/details/prayerbookreligi00lasauoft)
3. [Hymn and prayer book : for the use of such Lutheran churches as use the English language (1795)](https://archive.org/details/hymnprayerbo00kunz)

If you just want to use the King James Bible, start the program like this:

```
$ env/bin/python decode.py bible-kjv.txt
```

If you want to use other texts, put them in the `corpora` subdirectory
and supply just the filename on the command line.


### Command line flags

The program uses Viterbi decoding and assumes a "noisy
channel"--meaning that it assumes there's a chance the letters you
give it as input are wrong.  By default it assumes there's a 0.1%
chance of an error.  If you want to change that, use the
`--error_prob` flag.  For example, this tells it there's a 50% chance
of an error per letter:

```
$ env/bin/python decode.py --error_prob=0.5 bible-kjv.txt
```
