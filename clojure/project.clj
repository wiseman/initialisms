(defproject com.lemonodor.initialism "0.1.0-SNAPSHOT"
  :description "FIXME: write description"
  :url "http://example.com/FIXME"
  :license {:name "Eclipse Public License"
            :url "http://www.eclipse.org/legal/epl-v10.html"}
  :dependencies [[clojure-opennlp "0.3.2"]
                 [com.lemonodor.viterbi "0.1.0"]
                 [com.taoensso/timbre "2.7.1"]
                 [org.clojure/clojure "1.5.1"]]
  :main ^:skip-aot initialism.core
  :target-path "target/%s"
  :jvm-opts ["-Xmx8G"]
  :profiles {:uberjar {:aot :all}})
