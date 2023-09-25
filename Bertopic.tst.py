from bertopic import BERTopic
from bertopic.vectorizers import ClassTfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords
import PDButils as u
import pandas as pd
import spacy
from markdown_plain_text.extention import convert_to_plain_text

nlp = spacy.load("ru_core_news_lg")

text = """Ещё одна интересная классификация визуализаций попалась.
Автор - Koen van den Eeckhout.
Идея классификации интересная, но все же, не идеально. Наверное, облака или диаграмма венна была бы тут умесинее.
Например, что делать с печатными картами? Коварные карты бывают совершенно всех трех видов
**😁**
Но для подумать пригодится, чтобы для себя на старте ответить на вопросы:
- А какой же продукт мы хотим?
- Как быстро его должен воспринимать читатель?
- Как и кто будет с ним взаимодействовать?
Источник тут (впн):
"""

# only select necessary pipeline components to speed up processing

with nlp.select_pipes(enable=['tok2vec', "parser", "senter"]):
    doc = nlp(text)
    
for sentence in doc.sents:
    print("-"*100)
    print(sentence)

def expl_sent(text):
     with nlp.select_pipes(enable=['tok2vec', "parser", "senter"]):
          doc = nlp(text)
     return  [str(sentence) for sentence in doc.sents  ]

sql_query = pd.read_sql_query (f"""
                                                               SELECT
                                    id
                                    ,markdown
                               FROM content
                               where 
                                    m_length > 100 
                                 and markdown not like '%00:00%' 
                                -- and markdown not like '% и %' 
                                 --and markdown not like '% не %' 
                                 and id in (select id
                                                    from NTN_V_url where  url like '%t.me%') 

                                --limit 500              
                               """, u.DB_CONNECTION)

df_docs = pd.DataFrame(sql_query, columns = ['id', 'markdown']).replace(r"\[(.+)\]\(.+\)", '', regex=True).replace(r'http\S+', '', regex=True)
df_docs['sent'] = df_docs['markdown'].apply(convert_to_plain_text).apply(expl_sent)
df_docs=df_docs.explode('sent')

print(df_docs)


ctfidf_model = ClassTfidfTransformer(reduce_frequent_words=True)
my_stopwords = stopwords.words("russian")
vectorizer_model = CountVectorizer(stop_words=my_stopwords)

topic_model = BERTopic(language="multilingual"
                       ,ctfidf_model=ctfidf_model
                         ,vectorizer_model=vectorizer_model
                       )
topics, probs = topic_model.fit_transform(df_docs['sent'])
# print(topic_model.get_topic_info(df_docs['sent']))

topic_model.get_document_info(df_docs['sent']).to_excel(r'BERTopic.xlsx')

