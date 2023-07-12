
# -*- coding: utf-8 -*-
from newspaper import Article
import spacy
# for eng
from spacy.lang.en.stop_words import STOP_WORDS
# for russ and eng
from nltk.corpus import stopwords
from string import punctuation
from heapq import nlargest
import nltk
import argparse
# nltk.download("stopwords")
import re
import sys
import json
import trafilatura
import os
storeFolder = os.path.dirname(__file__) + os.sep + "results" + os.sep 

# Instantiate the parser
parser = argparse.ArgumentParser()
parser.add_argument('url')
args = parser.parse_args()

url = args.url

# url = 'https://habr.com/ru/post/696274/'
# url = 'https://github.com/coder/code-server/blob/71a127a62befeff1d55efe70be8f182e01cb29b6/docs/README.md'

# url = "https://habr.com/ru/post/664000/"
# url = "https://habr.com/ru/company/flant/blog/691388/"
# url = "https://medium.com/analytics-vidhya/text-summarization-using-spacy-ca4867c6b744"
# url = "https://habr.com/ru/post/683674/"

# url="https://betterhumans.pub/how-to-boost-your-productivity-for-scientific-research-using-obsidian-fe85c98c63c8"


article = Article(url)
article.download()
article.parse()

text = str(article.text)



downloaded = trafilatura.fetch_url(url)
text=trafilatura.extract(downloaded
# ,include_images=True
,include_formatting=True
# , include_links=True
# ,favor_precision=True
)


# p= re.compile(r"([^\,\?\;\:\.\!\.])\n$", flags=re.M)
p= re.compile(r"([^\,\?\;\:\.\!\.])$", flags=re.M)
text= p.sub(r"\g<1>.",text)
p= re.compile(r"([\?\;\.\!\.]) ", flags=re.M)
text= p.sub(r"\g<1>\n",text)
p= re.compile(r"([\?\;\.\!\.])([^\\S])", flags=re.M)
text= p.sub(r"\g<1> \g<2>",text)

text = re.sub(r'\n+', '\n', text)

russian_stopwords = stopwords.words("russian")
english_stopwords = stopwords.words("english")
cust_stopwords = ['её']
all_stopwords = russian_stopwords + english_stopwords + list(STOP_WORDS)  + list(cust_stopwords)
# + list("SELECT FROM WHERE JOIN GROUP ORDER BY COALESCE CASE WHEN ELSE LEFT AND NOT DESC END".lower().split())

punctuation = punctuation  + '\n' + "“”" + "’‘" + "—" + "…"

# create multilang nlp processing
if article.meta_lang == "ru":
    nlp = spacy.load('ru_core_news_md')
else:
    nlp = spacy.load("en_core_web_md")

doc= nlp(text)



word_frequencies={}
for word in doc:
    if word.lemma_.lower() not in all_stopwords:
        if word.lemma_.lower() not in punctuation:
            if word.lemma_.lower() not in word_frequencies.keys():
                word_frequencies[word.lemma_.lower()] = 1
            else:
                word_frequencies[word.lemma_.lower()] += 1
            # it's some trick to create only valueable summary
            if word.pos_ == "X":
                word_frequencies[word.lemma_.lower()] += -6
            if word.pos_ == "NUM":
                word_frequencies[word.lemma_.lower()] += -1
            # print(word.text, word.lemma_, word.pos_, word.tag_, word.dep_, word.shape_, word.is_alpha, word.is_stop)
max_frequency=max(word_frequencies.values())

save_word_frequencies_count =sorted(word_frequencies.items(), key=lambda item: item[1], reverse=True)

for word in word_frequencies.keys():
    word_frequencies[word]=word_frequencies[word]/max_frequency
sentence_tokens= [sent for sent in doc.sents]
sentence_scores = {}
for sent in sentence_tokens:
    # print(sent)
    # print('\n---\n')
    for word in sent:
        if word.lemma_.lower() in word_frequencies.keys():
            if sent not in sentence_scores.keys():                            
                sentence_scores[sent]=word_frequencies[word.lemma_.lower()]
            else:
                sentence_scores[sent]+=word_frequencies[word.lemma_.lower()]
exp_length = int(len(sentence_tokens)*0.025)
select_length = 5 if exp_length < 5 else exp_length

summary=nlargest(select_length, sentence_scores,key=sentence_scores.get)
final_summary=[word.text for word in summary]
# replace \n in json 
summary=''.join(final_summary).replace('\n',' ')



# top N Words
word_frequencies_seq= sorted(word_frequencies.items(), key=lambda item: item[1], reverse=True)
topn_word_fr = word_frequencies_seq[0:10]

# sys.stdout.reconfigure(encoding='utf-8')
# print('{ "summary" :' + '"%s"' % summary.replace('"','\\"')+ ",")
# print(' "words_length" :' + str(len(topn_word_fr))+ ",")
# print(' "words":' + json.dumps([ { "key": key , "value": value}  for key, value in topn_word_fr], ensure_ascii=False) + "}")
# print(summary)

f = open(storeFolder + "articleSimpleSummaryRU_EN_CLI.json", "w", encoding="utf-8")
f.write('{ "summary" :' + '"%s"' % summary.replace('"','\\"')+ ",")
f.write(' "words_length" :' + str(len(topn_word_fr))+ ",")
f.write(' "words":' + json.dumps([ { "key": key , "value": value}  for key, value in topn_word_fr], ensure_ascii=False) + "}")
f.close()
