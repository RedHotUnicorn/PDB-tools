
# https://stackoverflow.com/questions/28618400/how-to-identify-the-subject-of-a-sentence 


import trafilatura
import csv
import spacy
from   spacy import displacy
from spacy.tokenizer import Tokenizer
import re

url="https://microsoft.github.io/lida/"
url = "https://habr.com/ru/articles/696274/"
# url ="https://rxresu.me/"
# url = "https://stackoverflow.com/a/69178995"

downloaded = trafilatura.fetch_url(url)


# f = open("ini.html", "w")
# f.write(downloaded)
# f.close()




# 
# https://github.com/adbar/trafilatura/issues/351
sent=trafilatura.extract(downloaded.replace("</code>", "</code>```").replace("<code", "```<code")
	#, output_format='xml'
# ,include_images=True
 ,include_formatting=True
, include_links=True
# ,favor_precision=True
,include_comments=True
).replace('```', "\n```")

# f = open("rep.html", "w")
# f.write(downloaded)
# f.close()


# .replace("</code>", "'''").replace("<code>", "'''")

# sent=trafilatura.extract(sent)

# sent=trafilatura.html2txt(downloaded)

# sent= re.sub(r'```', r"\n```\n", sent , re.MULTILINE)



f = open("1.md", "w",encoding='utf-8')
f.write(sent)
f.close()




# nlp = spacy.load('ru_core_news_md')
# nlp=spacy.load('xx_sent_ud_sm')
nlp=spacy.load('ru_core_news_lg') 
# nlp=spacy.load('en_core_web_lg') 
# nlp=spacy.load('en_core_web_trf') 


nlp.tokenizer = Tokenizer(nlp.vocab, token_match=re.compile(r'(\n|\\n)```[\w]*?(\n|\\n)([\s\S]*?)(\n|\\n)```(\n|\\n)').search )

doc=nlp(sent)

sub_toks = [tok for tok in doc if (tok.dep_ == "nsubj") ]
sub_toks_lemma = [tok.lemma_.lower() for tok in doc if (tok.dep_ == "nsubj") ]

pos_lemma = [tok.lemma_.lower() for tok in doc if (tok.pos_ == "PROPN") ]
print("spacy") 
print(sub_toks) 
print("spacy lemma") 
print(sub_toks_lemma) 

print("pos_lemma") 
print(pos_lemma)
print("--"*60)

with open('spacy.csv', 'w', newline='',encoding='utf-8') as csvfile:
	spamwriter = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)
	spamwriter.writerow(["token.text", "token.lemma_"," token.pos_"," token.tag_"," token.dep_","token.shape_"," token.is_alpha"," token.is_stop"])
	print("{0:20}{1:20}{2:20}{3:20}{4:20}{5:20}{6:20}{7:20}".format("token.text", "token.lemma_"," token.pos_"," token.tag_"," token.dep_","token.shape_"," token.is_alpha"," token.is_stop"))
	for token in doc:
		if (token.pos_ != "SPACE"):
			print("{0:20}{1:20}{2:20}{3:20}{4:20}{5:20}{6:20}{7:20}".format(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,token.shape_, token.is_alpha, token.is_stop))
			spamwriter.writerow([token.text, token.lemma_, token.pos_, token.tag_, token.dep_,token.shape_, token.is_alpha, token.is_stop])

print("--"*60)

for ent in doc.ents:
    print("{0:20}{1:20}{2:20}{3:20}".format(ent.text, ent.start_char, ent.end_char, ent.label_))



svg = displacy.render(doc, style="ent", page=True)
open("displacy.html", "w", encoding="utf-8").write(svg)

from rake_nltk import Rake
import nltk
# nltk.download()
rake = Rake()

kw = rake.extract_keywords_from_text(sent)

ranked_phrases = rake.get_ranked_phrases()

print("rake_nltk") 
print(ranked_phrases)


# https://stackoverflow.com/questions/64111377/remove-markdown-code-block-from-python-string
