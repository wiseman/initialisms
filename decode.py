import collections
import logging
import os.path
import re
import sys
import time

import gflags
import nltk
import nltk.tokenize
from nltk.corpus import gutenberg

import viterbi

FLAGS = gflags.FLAGS
logger = logging.getLogger(__name__)

gflags.DEFINE_float(
  'error_prob',
  0.001,
  'The probability that a letter was read or written incorrectly.')


class Error(Exception):
  pass


ALPHANUM_RE = re.compile(r'[^a-z0-9]')


def is_alphanum(s):
  return not(ALPHANUM_RE.search(s))


def reposses(tokens):
  last_token = None
  for token in tokens:
    if not last_token:
      last_token = token
    elif token == "'s":
      yield last_token + token
      last_token = None
    else:
      yield last_token
      last_token = token


class Pdist(dict):
  "A probability distribution estimated from counts."
  def __init__(self, data=[], N=None, missingfn=None):
    for key, count in data:
      self[key] = self.get(key, 0) + int(count)
    self.N = float(N or sum(self.itervalues()))
    self.missingfn = missingfn or (lambda k, N: 1. / N)

  def __call__(self, key):
    if key in self:
      return self[key] / self.N
    else:
      return self.missingfn(key, self.N)


CORPUS_ROOT = os.path.join(os.path.dirname(__file__), 'corpora')


class Decoder(object):
  def __init__(self, corpora_ids, error_prob=None):
    self.error_prob = error_prob or FLAGS.error_prob
    extra_corpora = nltk.corpus.PlaintextCorpusReader(CORPUS_ROOT, '.*')
    words = []
    for corpus_id in corpora_ids:
      logger.info('Loading corpus %s', corpus_id)
      corpus = extra_corpora.raw(corpus_id)
      for sentence in nltk.tokenize.sent_tokenize(corpus):
        sent_words = [w.lower()
                      for w in reposses(nltk.tokenize.word_tokenize(sentence))]
        sent_words = [filter(is_alphanum, w) for w in sent_words]
        sent_words = [w for w in sent_words if w]
        sent_words = ['$'] + sent_words
        words += sent_words
    self.states = set(words)
    self.Pw = Pdist(collections.Counter(nltk.ngrams(words, 1)).items())
    self.P2w = Pdist(collections.Counter(nltk.ngrams(words, 2)).items())
    self.words_by_letter = collections.defaultdict(set)
    for w in words:
      self.words_by_letter[w[0]].update([w])
    logger.info('%s maximum possible states', len(self.states))

  def start_p(self, word):
    prob = self.Pw((word,))
    return prob

  def transition_p(self, prev, word):
    try:
      a = self.P2w[(prev, word)]
      b = self.Pw[(prev,)]
      return a / float(b)
    except KeyError:
      return self.Pw((word,))

  def emission_p(self, word, letter):
    if word[0] == letter:
      return 1.0 - self.error_prob
    else:
      return self.error_prob / 27.0  # a-z and $

  def decode(self, initials):
    timer = Timer()
    states = set()
    for obs in initials:
      states.update(self.words_by_letter[obs])
    logger.info('%s possible states', len(states))
    result = viterbi.viterbi(
      initials,
      states,
      self.start_p,
      self.transition_p,
      self.emission_p)
    logger.info('Took %s s', timer.elapsed())
    return result


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


def main(argv):
  args = FLAGS(argv)[1:]
  logging.basicConfig(level=logging.INFO)
  if not args:
    sys.stderr.write('Must give corpora names\n')
    sys.exit(1)
  logger.info('Initializing...')
  decoder = Decoder(args)
  while True:
    line = raw_input('Enter initials:\n').lower()
    logger.info('Decoding %r', line)
    result = decoder.decode(line)
    print result


if __name__ == '__main__':
  main(sys.argv)
