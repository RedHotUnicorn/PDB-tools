from bertopic import BERTopic
from bertopic.vectorizers import ClassTfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords
import pandas as pd
import spacy
from markdown_plain_text.extention import convert_to_plain_text  # https://github.com/kostyachum/python-markdown-plain-text
import re
import emoji
import _utils as u
import sqlite3

import string



pd.options.display.width = 0
pd.options.display.width = 1500
pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)

nlp = spacy.load("ru_core_news_lg")





text = """*Ещё* одна интересная классификация визуализаций попалась.
# Автор - Koen van den Eeckhout.
Идея классификации интересная, но все же, не идеально. Наверное, облака или диаграмма венна была бы тут уместнее.
Например, что делать с печатными картами? Коварные карты бывают совершенно всех трех видов
**😁**
Но для подумать пригодится, ~~чтобы~~ для себя на старте ответить на вопросы:
- [test](https://docs.python.org/3/tutorial/datastructures.html)
- https://docs.python.org/3/tutorial/datastructures.html
- А какой же продукт мы хотим?
- Как быстро его должен воспринимать читатель?
- Как и кто будет с ним взаимодействовать?
Источник тут (впн):
> quotes
__This is bold text__
"""


text = """
Статей о работе с PostgreSQL и её преимуществах достаточно много, но не всегда из них понятно, как следить за состоянием базы и метриками, влияющими на её оптимальную работу. В статье подробно рассмотрим SQL-запросы, которые помогут вам отслеживать эти показатели и просто могут быть полезны как пользователю.
## Зачем следить за состоянием PostgreSQL?
Мониторинг базы данных также важен, как и мониторинг ваших приложений. Необходимо отслеживать процессы более детализировано, чем на системном уровне. Для этого можно отслеживать следующие метрики:
Насколько эффективен кэш базы данных?
Какой размер таблиц в вашей БД?
Используются ли ваши индексы?
И так далее.
## Мониторинг размера БД и её элементов
### 1. Размер табличных пространств

```
SELECT spcname, pg_size_pretty(pg_tablespace_size(spcname))
FROM pg_tablespace
WHERE spcname<>'pg_global';
```
После запуска запроса вы получите информацию о размере всех tablespace созданных в вашей БД. Функция **pg_tablespace_size** предоставляет информацию о размере tablespace в байтах, поэтому для приведения к читаемому виду мы также используем функцию **pg_size_pretty**. Пространство pg_global исключаем, так как оно используется для общих системных каталогов.
### 2. Размер баз данных

```
SELECT pg_database.datname,
pg_size_pretty(pg_database_size(pg_database.datname)) AS size
FROM pg_database
ORDER BY pg_database_size(pg_database.datname) DESC;
```
После запуска запроса вы получите информацию о размере всех баз данных, созданных в рамках вашего экземпляра PostgreSQL.

"""



data = {

"id": [1] ,
"markdown" : [text]
}



data = pd.read_sql_query (f"""
                              SELECT
                                          id
                                        , markdown
                              FROM     content
                              WHERE    m_length   > 100 
                                   and markdown not like '%00:00%' 
                                   and id             in (select id from NTN_V_url where  url like '%t.me%')       
                              LIMIT 10  
                              """, sqlite3.connect(r'') )




def clean_text(rubbish_text):
    text_wo_emoji   = emoji.replace_emoji(rubbish_text, '')
    text_wo_code    = re.sub(r"```[^\S\r\n]*[a-z]*\n.*?\n```", ' INNER_CODE_BLOCK.', text_wo_emoji, 0, re.DOTALL)
    text_wo_md      = convert_to_plain_text(text_wo_code)                                                                # pd.DataFrame(data, columns = ['id', 'markdown']).replace(r"\[(.+)\]\(.+\)", '', regex=True).replace(r'http\S+', '', regex=True)  
    text_wo_links   = re.sub('http\S+','' ,text_wo_md)

    text_wo_uchars  = re.sub("[^\w.,!?\n]", " ", text_wo_links)     
    
    text_wo_dblspc  = re.sub(' {2,}', ' ', text_wo_uchars)                                                                 # https://stackoverflow.com/a/71340209/5353177

    lines           = text_wo_dblspc.split("\n") 
 
    # Add dot in the end of sent
    for i, l in enumerate(lines):
        if not l.endswith(tuple(string.punctuation)):
            lines[i] = l.strip() + '.'

    # Filter sent if it's not contain words
    lines           = [l for l in lines if l.strip(string.punctuation).replace(" ", "") != '']

    text_w_punct    = ' '.join(lines)

    # print(text_w_punct)
    # print('-'* 400)

    text            = text_w_punct
    return text




# Explode markdown to sentences
def expl_sent(text,num_of_sent = 3):
    with nlp.select_pipes(enable=['tok2vec', "parser", "senter"]):
          doc = nlp(text)
    sent = [str(sentence) for sentence in doc.sents  ]  

    
    # sent3= list(zip( sent[0:],sent[1:],sent[2:] ))
    # return [" ".join(map(str,item)) for item in sent3]  

    zip_arg = []
    for i in range(0,num_of_sent ):
        if len(sent) > i:
            zip_arg.append(sent[i:]) 
    sentN= list(zip( *zip_arg )) 

    return [" ".join(map(str,item)) for item in sentN]     



df_docs             = pd.DataFrame(data, columns = ['id', 'markdown'])
df_docs['sent']     = df_docs['markdown'].apply(clean_text).apply(expl_sent)
df_docs             = df_docs.explode('sent',ignore_index=True)

# print(df_docs['sent'])






def lemmatize(text: str):
     doc = nlp(text.lower())
     lemmas = []
     for token in doc:
          lemmas.append(token.lemma_)
     return lemmas


ctfidf_model        = ClassTfidfTransformer(reduce_frequent_words=True)
my_stopwords        = stopwords.words("russian")
vectorizer_model    = CountVectorizer(stop_words=my_stopwords,tokenizer=lemmatize)

topic_model         = BERTopic(  language           = "multilingual"
                                ,ctfidf_model       = ctfidf_model
                                ,vectorizer_model   = vectorizer_model
                                )
topics, probs       = topic_model.fit_transform(df_docs['sent'])
# print(topic_model.get_topic_info(df_docs['sent']))

res                 = topic_model.get_document_info(df_docs['sent'])
df_topics           = pd.DataFrame(topic_model.get_topics().items(), columns=['Topic', 'Words']) 
print(df_topics)

# print(res)
# res.to_excel(r'out/BERTopic.xlsx')

df_joined           = df_docs[['id']].join(res[['Topic' , 'Name','Representation']].query('Topic >= 0'))
df_joined['Topic']  = df_joined['Topic'].fillna(-1.0).astype(int)
df_joined           = df_joined.query('Topic >= 0')



gr_id               = df_joined.groupby(['id'])
gr_id_topic         = df_joined.groupby(['id','Name','Topic'])

count_by_id_topic   = gr_id_topic.agg({'Topic': 'count'}).rename(columns={'Topic': 'count_by_id_topic'})
count_by_id         = gr_id.size().to_frame(name = 'count_by_id')                                                                                               
count_unique_by_id  = gr_id.agg({'Topic': 'nunique'}).rename(columns={'Topic': 'count_unique_by_id'})

res_stat            = (  count_by_id 
                        .join(count_by_id_topic)
                        .join(count_unique_by_id)
                        # .join(df_topics.set_index('Topic') ,on = 'Topic',)
                      )   
res_stat['perc_count'] = res_stat['count_by_id_topic'] / res_stat['count_by_id']
print(res_stat)


res_stat            = res_stat.query('count_unique_by_id < 3 or perc_count > 0.1')
print(res_stat)



