(ns initialism.core
  (:require
   [clojure.java.io :as io]
   [clojure.string :as string]
   [com.lemonodor.viterbi :as viterbi]
   [opennlp.nlp :as nlp]
   [taoensso.timbre :as log])
  (:gen-class))


(defmacro log-time
  "Evaluates expr and logs the time it took.  Returns the value of expr."
  [msg expr]
  `(let [start# (. System (nanoTime))
         ret# ~expr]
     (log/info
      ~msg
      "took"
      (/ (double (- (. System (nanoTime)) start#)) 1000000000.0)
      "s")
     ret#))


(defn get-sentence-detector []
  (nlp/make-sentence-detector
   (io/resource "en-sent.bin")))


(defn reposess [tokens]
  (loop [last-token nil
         tokens tokens
         new-tokens []]
    (if (not (seq tokens))
      (if last-token
        (conj new-tokens last-token)
        new-tokens)
      (let [token (first tokens)
            rest-tokens (rest tokens)]
        (if (not last-token)
          (recur token rest-tokens new-tokens)
          (if (= token "'s")
            (recur nil rest-tokens (conj new-tokens (str last-token token)))
            (recur token rest-tokens (conj new-tokens last-token))))))))


(defn is-alphanum [token]
  (re-matches #"[A-Za-z0-9']+" token))


(defn get-tokenizer []
  (comp
   #(filter is-alphanum %)
   reposess
   #(map string/lower-case %)
   (nlp/make-tokenizer
    (io/resource "en-token.bin"))))


(defn n-grams [n tokens]
  (partition n 1 tokens))


(defn pdist [freqs]
  {:n (float (reduce + (map second freqs)))
   :freqs freqs})

(defn pdist-prob [pdist key]
  (let [{:keys [freqs n]} pdist]
    (get freqs key (/ 0.5 n))))


(defn read-corpus [sentencizer tokenizer corpus]
  (log/info "Loading corpus" corpus)
  (let [sentences (sentencizer (slurp corpus))
        tokens (apply concat
                      (pmap (fn [s]
                              (concat ["$"] (tokenizer s)))
                            sentences))
        stats {:unigrams (frequencies tokens)
               :bigrams (frequencies (n-grams 2 tokens))}]
    (log/info "Finished analyzing corpus" corpus)
    stats))


(defn merge-corpus-stats [s1 s2]
  {:unigrams (merge-with + (s1 :unigrams) (s2 :unigrams))
   :bigrams (merge-with + (s1 :bigrams) (s2 :bigrams))})


(defn read-corpora [corpora]
  (log-time (str "Loading " (count corpora) " corpora")
    (let [sentencizer (get-sentence-detector)
          tokenizer (get-tokenizer)
          stats (reduce
                 merge-corpus-stats
                 (pmap (partial read-corpus sentencizer tokenizer) corpora))]
      (assoc stats
        :P2w (pdist (stats :bigrams))
        :Pw (pdist (stats :unigrams))))))


(defn make-initialism-hmm [stats obs]
  (let [states (filter #(contains? (set obs) (first %))
                       (map first (stats :unigrams)))
        start-p (stats :Pw)
        trans-p (stats :P2w)]
    (log/info (count states) "distinct states")
    (viterbi/make-hmm
     :states states
     :start-p #(pdist-prob start-p %)
     :trans-p #(pdist-prob trans-p (list %1 %2))
     :emit-p (fn [word letter]
               (if (= (first word) letter)
                 1.0
                 0.0)))))


(defn -main
  "I don't do a whole lot ... yet."
  [& args]
  (let [stats (read-corpora args)]
    (loop [line (string/lower-case (read-line))]
      (when-not line
        (System/exit 0))
      (let [line (string/lower-case line)]
        (log/info "Decoding" line)
        (let [[prob words] (log-time (str "Decoding" line)
                             (viterbi/viterbi (make-initialism-hmm stats line) line))]
          (println prob (string/join " " words))))
      (recur (read-line)))))
