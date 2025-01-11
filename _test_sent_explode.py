from bertopic import BERTopic
from bertopic.vectorizers import ClassTfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords
import pandas as pd
import spacy
from markdown_plain_text.extention import convert_to_plain_text  # https://github.com/kostyachum/python-markdown-plain-text
import re
import emoji
import _utils_old as u
import sqlite3

import string



pd.options.display.width = 0
pd.options.display.width = 1500
pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)

nlp = spacy.load("ru_core_news_lg")

# text = """Мелкое.
# Механизм определения свой чужой во многом схож с механизмом работы Cloak, и позволяет достоверно определить подлинность клиента, но вместе с тем не вызываетподозренияуцензоровиустойчивкreplayатакамсосторонысистеманализатрафикаэтовыглядиткакподключениекнастоящемупопулярномусайту,серверотдаетнастоящийTLSсертификатэтогосайта,ивообще все включая TLS fingerprint сервера выглядит до предела аутентично и не вызывает подозрений. 
# Еще XTLS Reality может оказаться вариантом для обхода суровых корпоративных прокси с Man in the Middle, которые перешифровывают весь трафик из сети своим сертификатом нередко подобные прокси имеют список исключений для ресурсов с HSTS и certificate pinning, либо для экономии ресурсов, и подобрав правильный домен можно пролезть во внешнюю сеть без расшифровки трафика. 
# """

# data = {

# "id": [1] ,
# "markdown" : [text]
# }



data = pd.read_sql_query (f"""
                              SELECT
                                          c.id
                                        , markdown
                                        , url
                              FROM      content c
                              LEFT JOIN NTN_V_url n on n.id = c.id 
                              WHERE    m_length   > 10000 
                                   and markdown not like '%00:00%' 
                                   and c.id             in (select id from NTN_V_url where  
                                                                -- url like '%t.me%' or 
                                                                -- url like '%nesslabs.com%' or
                                                                url like '%habr.com%'
                                                            )    
                                    -- and    c.id = 36947
                              LIMIT 200
                              """, sqlite3.connect(r'C:\MyFiles\Code\PDB-tools\PDB-tools\results\articles.db') )




def clean_text(rubbish_text):
    text_wo_yaml    = re.sub(r"\A^---(.|\n)*?---", '', rubbish_text)
    text_wo_emoji   = emoji.replace_emoji(text_wo_yaml, '')
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
def expl_sent(text,num_of_sent = 3,max_sent_len = 100):
    # TODO guess what the lang of text
    try:
        with nlp.select_pipes(enable=['tok2vec', "parser", "senter"]):
            doc = nlp(text)
        sent = [str(sentence) for sentence in doc.sents  ]  


        # TODO if sentence is big try to reduce it by leaving only valuable words

        

    except Exception as e:
        print(e)
        print(len(text) + ' ' + text[0:100])

    old = sent
    # print(sent)
    # print('-'*200)

    for index, item in enumerate(sent):
        if len(item) > max_sent_len:
            
            right = 0
            left = 0
            new = []
            count = 0
            while right != len(item):
                left = right

                if right+max_sent_len <= len(item):
                    length = item[left:left+max_sent_len].rfind(' ')
                    if length == -1:
                        length = max_sent_len
                        # TODO what if two spaces?
                    right = left + length +1 # +1 bcs we want to skip last founded space in the next iteration
                else:
                    right = len(item)

                # print(right)
                # print(item[left:right])
                new.append(item[left:right])
                count+=1
                if count > 30 : 
                    print('ALERT')
                    print(item[left:right])

            # print(new)
            sent.pop(index)
            sent[index:index] = new

    # print('-'*200)
    # print(sent)

    # TODO implement this check 
    # print(''.join(old) == ''.join(sent))

                    

    
    # sent3= list(zip( sent[0:],sent[1:],sent[2:] ))
    # return [" ".join(map(str,item)) for item in sent3]  

    zip_arg = []
    for i in range(0,num_of_sent ):
        if len(sent) > i:
            zip_arg.append(sent[i:]) 
    sentN= list(zip( *zip_arg )) 

    return [" ".join(map(str,item)) for item in sentN]     



df_docs             = pd.DataFrame(data, columns = ['id', 'markdown','url'])
df_docs['sent']     = df_docs['markdown'].apply(clean_text).apply(expl_sent)
df_docs             = df_docs.explode('sent',ignore_index=True)

# print(df_docs['sent'])



df_docs.to_excel(r'out/df_docs.xlsx')





def lemmatize(text: str):
    # TODO mayb i should exclude some submodules of nlp spacy?

    nlp.max_length = len(text) + 1000
    with nlp.select_pipes(enable=['lemmatizer']):
        doc = nlp(text.lower())
    
    lemmas = []
    for token in doc:
        lemmas.append(token.lemma_)
    return lemmas


ctfidf_model        = ClassTfidfTransformer(reduce_frequent_words=True)
my_stopwords        = stopwords.words("russian") + stopwords.words("english")
vectorizer_model    = CountVectorizer(stop_words=my_stopwords,tokenizer=lemmatize)

topic_model         = BERTopic(  language           = "multilingual"
                                ,ctfidf_model       = ctfidf_model
                                ,vectorizer_model   = vectorizer_model
                                )
try:
    topics, probs       = topic_model.fit_transform(df_docs['sent'])
except Exception as e:
    print(e)

# print(topic_model.get_topic_info(df_docs['sent']))

res                 = topic_model.get_document_info(df_docs['sent'])
df_topics           = pd.DataFrame(topic_model.get_topics().items(), columns=['Topic', 'Words']) 
# print(df_topics)

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
                        .join(df_topics.set_index('Topic') ,on = 'Topic',)
                      )   
res_stat['perc_count'] = res_stat['count_by_id_topic'] / res_stat['count_by_id']
# print(res_stat)


res_stat            = res_stat.query('count_unique_by_id < 3 or perc_count > 0.15')
# print(res_stat)

res_stat.to_excel(r'out/BERTopic.xlsx')



