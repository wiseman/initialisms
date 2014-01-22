import collections
import itertools
import os.path
import re

import nltk
import nltk.tokenize
from nltk.corpus import gutenberg

import viterbi


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
  def __init__(self):
    extra_corpora = nltk.corpus.PlaintextCorpusReader(CORPUS_ROOT, '.*')
    words = []
    corpora = [
      nltk.corpus.gutenberg.raw('bible-kjv.txt'),
      #extra_corpora.raw('prayerbookreligi00lasauoft_djvu.txt'),
      #extra_corpora.raw('hymnprayerbo00kunz_djvu.txt')
    ]
    for corpus in corpora:
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
    print '%s maximum possible states' % (len(self.states),)

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
      return 1.0
    else:
      return 0.00000000000000000001

  def decode(self, initials):
    states = set()
    for obs in initials:
      states.update(self.words_by_letter[obs])
    print '%s possible states' % (len(states),)
    return viterbi.viterbi(
      initials,
      states,
      self.start_p,
      self.transition_p,
      self.emission_p)


def main():
  print 'Initializing...'
  decoder = Decoder()
  while True:
    line = raw_input('Ready\n')
    print 'Decoding %r' % (line,)
    result = decoder.decode(line)
    print '==>', result


if __name__ == '__main__':
  main()
