import math


# Helps visualize the steps of Viterbi.
def print_dptable(V):
  s = "    " + " ".join(("%7d" % i) for i in range(len(V))) + "\n"
  for y in V[0]:
    s += "%.15s: " % y
    s += " ".join("%.7s" % ("%f" % v[y]) for v in V)
    s += "\n"
  print(s)


def viterbi(obs, states, start_p, trans_p, emit_p):
  V = [{}]
  path = {}

  # Initialize base cases (t == 0)
  for y in states:
    V[0][y] = math.log10(start_p(y)) + math.log10(emit_p(y, obs[0]))
    path[y] = [y]

  # alternative Python 2.7+ initialization syntax
  # V = [{y:(start_p[y] * emit_p[y][obs[0]]) for y in states}]
  # path = {y:[y] for y in states}

  # Run Viterbi for t > 0
  for t in range(1, len(obs)):
    print '---- %s%%' % (int(100.0 * (float(t) / len(obs))),)
    V.append({})
    newpath = {}

    for i, y in enumerate(states):
      if i % 200 == 0:
        print i, y
      (prob, state) = max(
        (V[t - 1][y0] +
         math.log10(trans_p(y0, y)) +
         math.log10(emit_p(y, obs[t])), y0)
        for y0 in states)
      V[t][y] = prob
      newpath[y] = path[state] + [y]

    # Don't need to remember the old paths
    path = newpath

  #print_dptable(V)
  (prob, state) = max((V[t][y], y) for y in states)
  return (10.0 ** prob, path[state])


def example():
  states = ('Healthy', 'Fever')
  observations = ('normal', 'cold', 'dizzy')
  start_probability = {'Healthy': 0.6, 'Fever': 0.4}
  transition_probability = {
    'Healthy': {'Healthy': 0.7, 'Fever': 0.3},
    'Fever': {'Healthy': 0.4, 'Fever': 0.6},
  }
  emission_probability = {
    'Healthy': {'normal': 0.5, 'cold': 0.4, 'dizzy': 0.1},
    'Fever': {'normal': 0.1, 'cold': 0.3, 'dizzy': 0.6},
  }

  def start_p(s):
    return start_probability[s]

  def transition_p(s, n):
    return transition_probability[s][n]

  def emission_p(s, o):
    return emission_probability[s][o]

  return viterbi(observations,
                 states,
                 start_p,
                 transition_p,
                 emission_p)


if __name__ == '__main__':
  example()
