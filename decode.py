import collections
import logging
import os.path
import re
import sys
import time
import six
import gflags
import nltk
import nltk.tokenize
from nltk.corpus import gutenberg

import viterbi

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
  return not(TOKEN_RE.search(s))


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


class Pdist(dict):
  "A probability distribution estimated from counts."
  def __init__(self, data=[], N=None, missingfn=None):
    for key, count in data:
      self[key] = self.get(key, 0) + int(count)
    self.N = float(N or sum(self.values()))
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
    timer = Timer()
    for corpus_id in corpora_ids:
      logger.info('Loading corpus %s', corpus_id)
      corpus = extra_corpora.raw(corpus_id)
      print("this is the corpus", corpus)
      for sentence in nltk.tokenize.sent_tokenize(corpus):

        sent_words = [w.lower()
                      for w in reposses(nltk.tokenize.word_tokenize(sentence))]
    #     sent_words = [tuple(filter(is_token, w)) for w in sent_words]
    #     # print(f"sentence_words:\n {sent_words}")
    #     sent_words = [w for w in sent_words if w]
    #     if sent_words:
    #       sent_words = ['$'] + sent_words
    #       words.extend(sent_words)

    # # print(f"Words found:\n {words}")
    # self.states = set(words)

    # self.Pw = Pdist(collections.Counter(nltk.ngrams(words, 1)).items())
    # self.P2w = Pdist(collections.Counter(nltk.ngrams(words, 2)).items())
    # self.words_by_letter = collections.defaultdict(set)

    # for w in words:
    #   self.words_by_letter[w[0]].update([w])
    # # print(f" self.words_by_letter \n { self.words_by_letter }")

    # logger.info(
    #   'Loading %s corpora took %s s', len(corpora_ids), timer.elapsed())
    # logger.info('%s distinct tokens', len(self.states))

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
    
    logger.info('Searching %s possible states', len(states))
    
    # result = viterbi.viterbi(
    #   initials,
    #   states,
    #   self.start_p,
    #   self.transition_p,
    #   self.emission_p)
    logger.info('Decoding %r took %s s', initials, timer.elapsed())
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


def repl(decoder):
  try:
    while True:
      if sys.stdin.isatty():
        line = input('Enter initials:\n')
      else:
        line = input()
      logger.info('Decoding %r', line)
      prob, words = decoder.decode(line.lower())
      # print(' '.join(''.join(tup) for tup in words))
      print(prob, ' '.join(''.join(tup) for tup in words))
  except EOFError:
    pass


def dump_tokens(decoder):
  for word in sorted(decoder.states):
    print(word)


def main(argv):
  args = FLAGS(argv)[1:]
  logging.basicConfig(level=logging.INFO)
  if not args:
    sys.stderr.write('Must give corpora names\n')
    sys.exit(1)
  decoder = Decoder(args)
  if FLAGS.dump_tokens:
    dump_tokens(decoder)
  else:
    repl(decoder)


if __name__ == '__main__':
  main(sys.argv)
