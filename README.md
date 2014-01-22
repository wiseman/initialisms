# finalletters

This program guesses sentences from initial letters of each word using
the unreasonable effectiveness of data.  For example, given the input
"obv" it will output "o blessed virgin".

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
$ env/bin/python decode.py order-of-morning.txt
```

Once it says "Enter initials:", you can type something like
"OFWAIHHBTN" and press Enter.  A second later it will output something
like this:

```
(1.8416799947589708e-09, ['our', 'father', 'who', 'are', 'in', 'heaven', 'hallowed', 'be', 'thy', 'name'])
```

This means that its best guess for "OFWAIHHBTN" is "our father who are
in heaven hallowed be thy name", with a probability of some small
number.

This code is unoptimized and slow.  If you try to decode more than 3
or 4 characters with a larger corpus, you're going to be waiting a
long time.

You can use "$" to indicate the start of a sentence, for example "$obv".


### Corpora

The program makes its guesses based on text you feed it.  I've included five pieces of text:

1. [King James Bible](https://en.wikipedia.org/wiki/King_James_Version)
2. [Prayer-book for religious : a complete manual of prayers and devotions for the use of the members of all religious communities : a practical guide to the particular examen and to the methods of meditation (1914, c1904)](https://archive.org/details/prayerbookreligi00lasauoft)
3. [Hymn and prayer book : for the use of such Lutheran churches as use the English language (1795)](https://archive.org/details/hymnprayerbo00kunz)
4. [The Order of Morning Service](http://www.lutheran-hymnal.com/online/page5.html)
5. [The Lutheran Hymnal](http://www.projectwittenberg.org/etext/hymnals/tlh/)

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
