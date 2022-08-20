from itertools import permutations
import logging
import os.path
import re
import time
import gflags
import nltk
import nltk.tokenize

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
    def __init__(self, ordered):
        self.results_list = []
        self.ordered = ordered
        extra_corpora = nltk.corpus.PlaintextCorpusReader(CORPUS_ROOT, '.*')
        corpus = extra_corpora.raw("words.txt")
        print("this is the corpus (uncomment)")
        # print(corpus)
        self.corpus = corpus

    # Function to swap two characters in a character array
    def swap(self, ch, i, j):
        temp = ch[i]
        ch[i] = ch[j]
        ch[j] = temp
    
    # Recursive function to generate all permutations of a string
    def permutations(self, ch, curr_index=0):

        if curr_index == len(ch) - 1:
            print(''.join(ch))

        for i in range(curr_index, len(ch)):
            self.swap(ch, curr_index, i)
            self.permutations(ch, curr_index + 1)
            self.swap(ch, curr_index, i)

    # Regex to find sequence of words w/ first letters matching initials
    def createRegex(self, initials):

        seperator = "[\\s:;,–]*"
        rest_of_word = "[a-zA-Z0-9]+"
        customer_regex = "\\b"
        for letter in initials:
            temp_regex = letter + rest_of_word + seperator
            customer_regex += temp_regex
        customer_regex = customer_regex[:-len(seperator)]
        # print("customer_regex", customer_regex)

        return re.compile(customer_regex, re.IGNORECASE)

    # flattens array
    # drops all empty elements
    # TODO drop elements not the same length as the initials string
    def tidyResultsList(self):
        self.results_list = [item for sublist in self.results_list for item in sublist]
        self.results_list = [x for x in self.results_list if x]

    def decode(self, initials):
        timer = Timer()
        print("self.ordered =", self.ordered)
        if not self.ordered:
            all_permutations_of_initials = permutations(list(initials))
            for permutation in all_permutations_of_initials:
                print("permutation", permutation)
                regex = self.createRegex(permutation)
                self.results_list.append(regex.findall(self.corpus))
        else:
            regex = self.createRegex(initials)
            self.results_list.append(regex.findall(self.corpus))

        self.tidyResultsList()

        logger.info('Decoding %r took %s s', initials, timer.elapsed())
        return self.results_list
