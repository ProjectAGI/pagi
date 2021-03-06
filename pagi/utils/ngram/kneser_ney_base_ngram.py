# Copyright (C) 2019 Project AGI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""KneserNeyBaseNGram class."""

from pagi.utils.ngram import NGram


# pylint: disable-all
class KneserNeyBaseNGram(NGram):
  """"Kneser-Ney base n-gram class."""

  #def __init__(self, sents, n, corpus='', D=None):
  def __init__(self, sents, words, n, corpus='', estimate_D=False, discount=None):
    """
    sents -- list of sents
    n -- order of the model
    D -- Discount value
    """

    self.sos = '<s>'
    self.eos = '</s>'

    self.n = n  # Order (i.e. n-gram where n is the max order of n-gram model)
    self.D = -1  # Discount[s]
    self.corpus = corpus
    self.smoothingtechnique = 'Kneser Ney Smoothing'
    # N1+(·w_<i+1>)
    #self._N_dot_tokens_dict = N_dot_tokens = defaultdict(set)
    self._N_dot_tokens_dict = N_dot_tokens = DefaultDict(set)
    # N1+(w^<n-1> ·)
    #self._N_tokens_dot_dict = N_tokens_dot = defaultdict(set)
    self._N_tokens_dot_dict = N_tokens_dot = DefaultDict(set)
    # N1+(· w^<i-1>_<i-n+1> ·)
    #self._N_dot_tokens_dot_dict = N_dot_tokens_dot = defaultdict(set)
    self._N_dot_tokens_dot_dict = N_dot_tokens_dot = DefaultDict(set)
    #self.counts = counts = defaultdict(int)
    self.counts = counts = DefaultDict(int)
    vocabulary = []

    if estimate_D is True:
      pass  # Removed

    # discount value D provided
    # On correct usage:
    # https://stackoverflow.com/questions/35242155/kneser-ney-smoothing-of-trigrams-using-python-nltk
    # Also, it would seem you ignore the provided discount parameter... if none is given you search for the one which minimizes perplexity,
    #  but if one is given you don't use it.. you instead use some ad-hoc method of calculating it which is different than the one you use
    #  if none is given... This seems odd. – Mr.WorshipMe Jul 14 '16 at 19:44
    # @Mr.WorshipMe Regarding to the discount parameter, you are right, the documentation is not quite correct. Actually, the parameter D is
    #  a flag: if it is set to None (default), D will be computed as in the paper from where I took the algorithm. If it is not None, the
    #  algorithm will try a few values and use the one that gives better results. That said, the discount parameter answers the question
    #  "Would you like to compute D or just try different values and choose the better one?". Thank you for the comment, I will modify the
    #  script to avoid this kind of confusion. – Giovanni Rescia Jul 15 '16 at 18:39
    # @Mr.WorshipMe About the 0-gram count and "doing nothing with them", it is useful when you are working with unigrams, 0-grams
    #  (represented by ()) count how many words there are. And about of keeping the previous and next words for a token, it helped me for
    #  debugging; but I agree that keeping only the size of the set would be better. Any other comment, please do
    #  – Giovanni Rescia Jul 15 '16 at 18:52
    else:
      print('Using formulaic value ')

      use_sentences = False
      if use_sentences:
        # prefix and suffix sentences
        # Note it prefixes with SOS n-1 times, and suffix EOS once.
        sents = list(map(lambda x: [self.sos]*(n-1) + x + [self.eos], sents))

        # for-each sentence
        for sent in sents:
          #print('--> ', sent)
          # 0 <= j <= n  (because n+1, e.g. if n=5 then 0,1,2,3,4,5
          for j in range(n+1):  # all k-grams for 0 <= k <= n
            # n-j; if
            ia = n-j
            ib = len(sent) - j + 1
            # print('j ', j)
            # print('ia ', ia)
            # print('ib ', ib)
            for i in range(ia, ib):
              ngram = tuple(sent[i: i + j])
              #print('n-gram ', ngram)

              counts[ngram] += 1
              if ngram:
                if len(ngram) == 1:
                  vocabulary.append(ngram[0])  # append all single tokens - not unique yet
                else:
                  # e.g., ngram = (1,2,3,4,5,6,7,8)
                  # right_token = (8,)
                  # left_token = (1,)
                  # right_kgram = (2,3,4,5,6,7,8)
                  # left_kgram = (1,2,3,4,5,6,7)
                  # middle_kgram = (2,3,4,5,6,7)
                  right_token, left_token, right_kgram, left_kgram, middle_kgram =\
                      ngram[-1:], ngram[:1], ngram[1:], ngram[:-1], ngram[1:-1]
                  N_dot_tokens[right_kgram].add(left_token)
                  N_tokens_dot[left_kgram].add(right_token)
                  if middle_kgram:
                    N_dot_tokens_dot[middle_kgram].add(right_token)
                    N_dot_tokens_dot[middle_kgram].add(left_token)

          #input("Press Enter to continue...")

          # print('n: ', n)  # 5
          if n-1:
            #x = (self.sos,)*(n-1)
            #print('x?: ', x)
            # x?:  ('<s>', '<s>', '<s>', '<s>')
            counts[(self.sos,)*(n-1)] = len(sents)
      else:  # No sentences - stream
        print('Stream mode.')
        num_words = len(words)
        print('Have ', num_words, ' words.')
        padded_words = [self.sos]*(n-1) + words + [self.eos]
        for j in range(1, n+1):  # all k-grams for 0 <= k <= n
          print('Processing n=', j)
          # n-j; if
          ia = n-j
          ib = num_words - j + 1
          print('j ', j)
          print('ia ', ia)
          print('ib ', ib)
          for i in range(ia, ib):
            ngram = tuple(padded_words[i: i + j])
            #print('n-gram ', ngram)

            counts[ngram] += 1
            if ngram:
              if len(ngram) == 1:
                vocabulary.append(ngram[0])  # append all single tokens - not unique yet
              else:
                # e.g., ngram = (1,2,3,4,5,6,7,8)
                # right_token = (8,)
                # left_token = (1,)
                # right_kgram = (2,3,4,5,6,7,8)
                # left_kgram = (1,2,3,4,5,6,7)
                # middle_kgram = (2,3,4,5,6,7)
                right_token, left_token, right_kgram, left_kgram, middle_kgram =\
                    ngram[-1:], ngram[:1], ngram[1:], ngram[:-1], ngram[1:-1]
                N_dot_tokens[right_kgram].add(left_token)
                N_tokens_dot[left_kgram].add(right_token)
                if middle_kgram:
                  N_dot_tokens_dot[middle_kgram].add(right_token)
                  N_dot_tokens_dot[middle_kgram].add(left_token)

          #input("Press Enter to continue...")


      # Find unique set of tokens
      print('Finding unique token set...')
      self.vocab = set(vocabulary)  # 10,000 correct
      print('Vocab has size:', len(self.vocab))

      aux = 0
      for w in self.vocab:
        aux += len(self._N_dot_tokens_dict[(w,)])
      self._N_dot_dot_attr = aux

      if discount is None:
        # Citation for discount formula.
        # http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.310.4865&rep=rep1&type=pdf
        xs = [k for k, v in counts.items() if v == 1 and n == len(k)]
        ys = [k for k, v in counts.items() if v == 2 and n == len(k)]
        n1 = len(xs)
        n2 = len(ys)
        self.D = n1 / (n1 + 2 * n2)
        print('Using heuristic discount value ', self.D)
      else:
        self.D = float(discount)
        print('Using provided discount value ', self.D)

      # Alternative formula
      # Modified KN smoothing from Chen-Goodman
      # https://people.eecs.berkeley.edu/~klein/cs294-5/chen_goodman.pdf
      # via.
      # http://smithamilli.com/blog/kneser-ney/
      # https://github.com/smilli/kneser-ney/blob/master/kneser_ney.py
      # D(k,i) =
      n1 = len([k for k, v in counts.items() if v == 1 and n == len(k)])
      n2 = len([k for k, v in counts.items() if v == 2 and n == len(k)])
      n3 = len([k for k, v in counts.items() if v == 3 and n == len(k)])
      n4 = len([k for k, v in counts.items() if v == 4 and n == len(k)])
      print('n1: ', n1)
      print('n2: ', n2)
      print('n3: ', n3)
      print('n4: ', n4)
      Y = n1 / (n1 + 2 * n2)
      D1 = 1.0 - 2*Y*(n2/n1)
      D2 = 2.0 - 3*Y*(n3/n2)
      D3 = 3.0 - 4*Y*(n4/n3)
      self.D_mod = [D1, D2, D3]
      print("D_mod = ", self.D_mod)




  def optimize_discount(self, sents):
    #D_candidates = [i*0.12 for i in range(1, 9)]
    #D_candidates = [0.9, 0.9477, 0.95, 0.96, 0.98, 1.0, 1.1, 1.2]
    #D_candidates = [0.9, 0.9477, 0.95, 0.96, 0.98, 1.0, 1.05, 1.1, 1.15, 1.2, 1.25, 1.3, 1.4]
    #D_candidates = [1.0]  # 190
    #D_candidates = [1.1]  # 147
    #D_candidates = [1.2]  # 116
    D_candidates = [3]  # 10
    #xs = []
    for D in D_candidates:
      self.D = D
      print('Testing discount: ', self.D)
      aux_perplexity = self.perplexity(sents)
      print('Tested discount: ', self.D, ' PPL ', aux_perplexity, '\n')
      #xs.append((D, aux_perplexity))
      #xs.sort(key=lambda x: x[1])
    #self.D = xs[0][0]
    # with open('kneserney_' + str(n) + '_parameters_'+corpus, 'a') as f:
    #     f.write('Order: {}\n'.format(self.n))
    #     f.write('D: {}\n'.format(self.D))
    #     f.write('Perplexity observed: {}\n'.format(xs[0][1]))
    #     f.write('-------------------------------\n')
    # f.close()


  def V(self):
    """
    returns the size of the vocabulary i.e. number of unique tokens
    """
    return len(self.vocab)

  def N_dot_dot(self):
    """
    Returns the sum of N_dot_token(w) for all w in the vocabulary
    """
    return self._N_dot_dot_attr

  def N_tokens_dot(self, tokens):
    """
    Returns a set of words in which count(prev_tokens+word) > 0
    i.e., the different ngrams it completes
    tokens -- a tuple of strings
    """
    if not isinstance(tokens, tuple):
      raise TypeError('`tokens` has to be a tuple of strings')
    return self._N_tokens_dot_dict[tokens]

  def N_dot_tokens(self, tokens):
    """
    Returns a set of ngrams it completes
    tokens -- a tuple of strings
    """
    if not isinstance(tokens, tuple):
      raise TypeError('`tokens` has to be a tuple of strings')
    return self._N_dot_tokens_dict[tokens]

  def N_dot_tokens_dot(self, tokens):
    """
    Returns a set of ngrams it completes
    tokens -- a tuple of strings
    """
    if not isinstance(tokens, tuple):
      raise TypeError('`tokens` has to be a tuple of strings')
    return self._N_dot_tokens_dot_dict[tokens]

  # -------------------------------------------------------------------------
  # read-only versions (limit memory)
  # -------------------------------------------------------------------------
  def count_get(self, tokens):
    """Count for an n-gram or (n-1)-gram.
    tokens -- the n-gram or (n-1)-gram tuple.
    """
    #print('size: ', len(self.counts))
    return self.counts.get_and_forget(tokens)

  def N_tokens_dot_get(self, tokens):
    """
    Returns a set of words in which count(prev_tokens+word) > 0
    i.e., the different ngrams it completes
    tokens -- a tuple of strings
    """
    if type(tokens) is not tuple:
      raise TypeError('`tokens` has to be a tuple of strings')
    #return self._N_tokens_dot_dict[tokens]
    return self._N_tokens_dot_dict.get_and_forget(tokens)

  def N_dot_tokens_get(self, tokens):
    """
    Returns a set of ngrams it completes
    tokens -- a tuple of strings
    """
    if not isinstance(tokens, tuple):
      raise TypeError('`tokens` has to be a tuple of strings')
    #return self._N_dot_tokens_dict[tokens]
    return self._N_dot_tokens_dict.get_and_forget(tokens)

  def N_dot_tokens_dot_get(self, tokens):
    """
    Returns a set of ngrams it completes
    tokens -- a tuple of strings
    """
    if not isinstance(tokens, tuple):
      raise TypeError('`tokens` has to be a tuple of strings')
    #return self._N_dot_tokens_dot_dict[tokens]
    return self._N_dot_tokens_dot_dict.get_and_forget(tokens)
  # -------------------------------------------------------------------------
  # read-only versions (limit memory)
  # -------------------------------------------------------------------------

  def get_special_param(self):
    return "D", self.D
