(ns initialism.core
  (:require
   [clojure.java.io :as io]
   [clojure.string :as string]
   [com.lemonodor.gflags :as gflags]
   [com.lemonodor.viterbi :as viterbi]
   [opennlp.nlp :as nlp]
   [taoensso.timbre :as log])
  (:gen-class))


(gflags/define-boolean "dump-tokens"
  false
  "Dump a list of all tokens found in the corpora, then exit.")
(gflags/define-boolean "dump-hashes"
  false
  "Dump a list of hash frequencies for tokens and states, then exit.")
(gflags/define-boolean "trigram-mode"
  false
  "Show exact matches for trigrams")


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


(defn is-token [token]
  (re-matches #"[A-Za-z']+" token))


(defn get-tokenizer []
  (comp
   #(filter is-token %)
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


(defn corpus-stats [tokens]
  {:unigrams (frequencies tokens)
   :bigrams (frequencies (n-grams 2 tokens))
   :trigrams (frequencies (n-grams 3 tokens))})


(defn read-corpus [sentencizer tokenizer corpus]
  (log/info "Loading corpus" corpus)
  (let [sentences (sentencizer (slurp corpus))
        tokens (apply concat
                      (pmap (fn [s]
                              (let [tokens (tokenizer s)]
                                (if (seq tokens)
                                  (concat ["$"] tokens)
                                  '())))
                            sentences))]
    tokens))


(defn merge-corpus-stats [s1 s2]
  {:unigrams (merge-with + (s1 :unigrams) (s2 :unigrams))
   :bigrams (merge-with + (s1 :bigrams) (s2 :bigrams))
   :trigrams (merge-with + (s1 :trigrams) (s2 :trigrams))})


(defn read-corpora [corpora processor]
  (let [sentencizer (get-sentence-detector)
        tokenizer (get-tokenizer)
        stats (log-time (str "Loading " (count corpora) " corpora")
                (let [stats (reduce
                             merge-corpus-stats
                             (pmap (comp
                                    processor
                                    (partial read-corpus sentencizer tokenizer))
                                   corpora))]
                  (assoc
                      stats
                    :P2w (pdist (stats :bigrams))
                    :Pw (pdist (stats :unigrams)))))]
    (log/info (count (stats :unigrams)) "distinct tokens")
    stats))


(defn make-initialism-hmm [stats obs]
  (let [states (filter #(contains? (set obs) (first %))
                       (map first (stats :unigrams)))
        start-p (stats :Pw)
        trans-p (stats :P2w)]
    (log/info "Searching" (count states) "possible states")
    (viterbi/make-hmm
     :states states
     :start-p #(pdist-prob start-p %)
     :trans-p #(pdist-prob trans-p (list %1 %2))
     :emit-p (fn [word letter]
               (if (= (first word) letter)
                 1.0
                 0.0)))))


(defn repl [stats]
  (loop [line (string/lower-case (read-line))]
    (when-not line
      (System/exit 0))
    (let [line (string/lower-case line)]
      (log/info "Decoding" line)
      (let [[prob words] (log-time (str "Decoding " line)
                           (viterbi/viterbi (make-initialism-hmm stats line) line))]
        (println prob (string/join " " words))))
    (recur (read-line))))


(defn zip [& colls]
  (apply (partial map vector) colls))


(defn trigram-repl [stats]
  (let [trigram-freqs (:trigrams stats)
        initials-words-map
        (reduce (fn [initials-map [trigram _]]
                  (let [initials (string/join (nth (apply zip trigram) 0))]
                    (assoc
                        initials-map initials
                        (conj (get initials-map initials [])
                              [(trigram-freqs trigram) (vec trigram)]))))
                {}
                trigram-freqs)]
    (log/info (count trigram-freqs) "distinct trigrams")
    (loop [line (read-line)]
      (when-not line
        (System/exit 0))
      (let [line (string/lower-case line)]
        (log/info "Decoding" line)
        (doseq [[count trigram] (reverse (sort (initials-words-map line)))]
          (println count (string/join " " trigram)))
        (recur (read-line))))))


(defn dump-tokens [stats]
  (log/info "Dumping tokens")
  (doseq [[token count] (sort (stats :unigrams))]
    (println token)))


(defn dump-hashes [stats]
  (println "# unigrams")
  (doseq [[hash count] (frequencies (map hash (:unigrams stats)))]
    (println hash count))
  (println "# bigrams")
  (doseq [[hash count] (frequencies (map hash (:bigrams stats)))]
    (println hash count)))


(defn -main
  "I don't do a whole lot ... yet."
  [& args]
  (let [unparsed-args (gflags/parse-flags (concat [nil] args))
        flags (gflags/flags)
        stats (read-corpora unparsed-args corpus-stats)]
    (cond
     (flags :dump-tokens) (dump-tokens stats)
     (flags :dump-hashes) (dump-hashes stats)
     (flags :trigram-mode) (trigram-repl stats)
     :else (repl stats)))
  (System/exit 0))
