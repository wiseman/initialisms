import logging
import os.path
import re
import sys
import time
import gflags
import nltk
import nltk.tokenize
import json
from flask import Flask


application = app = Flask(__name__) # because aws looks for application


@app.route("/api/mnemonics_function/<initials>")
def returnListOfMnemonics(initials):
    decoder = Decoder()
    return decoder.decode(initials.lower())


FLAGS = gflags.FLAGS
logger = logging.getLogger(__name__)


gflags.DEFINE_float(
    'error_prob',
    0.000001,
    'The probability that a letter was read or written incorrectly.')
gflags.DEFINE_bool(
    'dump_tokens',
    False,
    'Dump a list of all tokens found in the corpora, then exit.')


class Error(Exception):
    pass


TOKEN_RE = re.compile(r'[^a-z\']')


def is_token(s):
    return not (TOKEN_RE.search(s))


def reposses(tokens):
    last_token = None
    for token in tokens:
        if not last_token:
            last_token = token
        elif token == "'s":
            yield last_token + token
            last_token = None
        elif token == "n't":
            yield last_token + token
            last_token = None
        else:
            yield last_token
            last_token = token
        if last_token:
            yield last_token


CORPUS_ROOT = os.path.join(os.path.dirname(__file__), 'corpora')


class Timer(object):
    """Keeps track of wall-clock time."""
    def __init__(self):
        self.start_time = None
        self.reset()

    def reset(self):
        """Resets the timer."""
        self.start_time = time.time()

    def elapsed(self):
        """Returns the elapsed time in seconds.

        Elapsed time is the time since the timer was created or last
        reset.
        """
        return time.time() - self.start_time


class Decoder(object):
    def __init__(self, error_prob=None):
        self.error_prob = error_prob or FLAGS.error_prob
        extra_corpora = nltk.corpus.PlaintextCorpusReader(CORPUS_ROOT, '.*')
        corpus = extra_corpora.raw("words.txt")
        print("this is the corpus (uncomment)")
        # print(corpus)
        self.corpus = corpus

    def createRegex(self, initials):

        seperator = "[\s:;,–]*"
        rest_of_word = "[a-zA-Z0-9]+"
        customer_regex = ""
        for letter in initials:
            temp_regex = letter + rest_of_word + seperator
            customer_regex += temp_regex
        customer_regex = customer_regex[:-len(seperator)]
        print("customer_regex", customer_regex)

        return re.compile(customer_regex, re.IGNORECASE)

    def decode(self, initials):
        timer = Timer()
        states = set()
        regex = self.createRegex(initials)

        logger.info('Searching %s possible states', len(states))
        
        result_list = regex.findall(self.corpus)
        logger.info('Decoding %r took %s s', initials, timer.elapsed())
        return json.dumps(result_list)


def repl(decoder):
    try:
        while True:
            if sys.stdin.isatty():
                line = input('Enter initials:\n')
            else:
                line = input()
            logger.info('Decoding %r', line)
            words = decoder.decode(line.lower())
            # print(' '.join(''.join(tup) for tup in words))
            print(' '.join(''.join(tup) for tup in words))
    except EOFError:
        pass


if __name__ == '__main__':
    app.run()

