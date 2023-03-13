import sumy 


from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

import json
import os
storeFolder = os.path.dirname(__file__) + os.sep + "results" + os.sep 
additionalFolder = os.path.dirname(__file__) + os.sep + "additional files" + os.sep 
LANGUAGE = "russian"
SENTENCES_COUNT = 1

f = open(storeFolder + "separateArticleToJSONHeaderAndText.json", "r", encoding="utf-8")
w = open(storeFolder + "sumyUseByEachHeader.md", "w", encoding="utf-8")


headers_and_text = json.loads(f.read())
for i in headers_and_text:
    w.write(i["header"]+ '\n')
    parser = PlaintextParser.from_string("\n".join(i["text"]), Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)

    summarizer = Summarizer(stemmer)
    # summarizer.stop_words = get_stop_words(LANGUAGE)
    f = open(additionalFolder + "russian_stopwords.txt", encoding='utf8')
    summarizer.stop_words = f.read()

    for sentence in summarizer(parser.document, SENTENCES_COUNT):
        w.write(str(sentence)+ '\n')
w.close()


# TODO need to parse all document and than collect best one