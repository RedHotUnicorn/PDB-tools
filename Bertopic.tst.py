from bertopic import BERTopic
from bertopic.vectorizers import ClassTfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer

import PDButils as u
import pandas as pd

INPUT_TBL_1     = 'content'

sql_query = pd.read_sql_query (f"""
                               SELECT
                                    id
                                    ,markdown
                               FROM {INPUT_TBL_1}
                               where  m_length > 100 and markdown not like '%00:00%' and markdown not like '% и %' and markdown not like '% не %' 
                                limit 500                       
                               """, u.DB_CONNECTION)

df_docs = pd.DataFrame(sql_query, columns = ['id', 'markdown']).replace(r"\[(.+)\]\(.+\)", '', regex=True).replace(r'http\S+', '', regex=True)

ctfidf_model = ClassTfidfTransformer(reduce_frequent_words=True)
vectorizer_model = CountVectorizer(stop_words="english")

topic_model = BERTopic(language="multilingual",ctfidf_model=ctfidf_model,vectorizer_model=vectorizer_model)
topics, probs = topic_model.fit_transform(df_docs['markdown'])

topic_model.get_document_info(df_docs['markdown']).to_excel(r'BERTopic.xlsx')

