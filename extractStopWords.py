

from nltk.corpus import stopwords
import nltk 
import os
storeFolder = os.path.dirname(__file__) + os.sep + "additional files" + os.sep 

# nltk.download()
russian_stopwords = stopwords.words("russian")
f = open(storeFolder + "russian_stopwords.txt", "w", encoding="utf-8")
f.write('\n'.join(map(str, russian_stopwords)))
f.close()

english_stopwords = stopwords.words("english")
f = open(storeFolder + "renglish_stopwords.txt", "w", encoding="utf-8")
f.write('\n'.join(map(str, english_stopwords)))
f.close()
