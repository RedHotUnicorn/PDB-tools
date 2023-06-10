import pandas as pd


import os
import sqlite3



storeFolder = os.path.dirname(__file__) + os.sep + "results" + os.sep 
csv_path = r'C:\Users\User\Downloads\notion.csv'

df = pd.read_csv(csv_path, usecols = ['property_url','url','property_create_dt','property_done'])
df['done'] = df.apply(lambda x: 0 if x.property_done == False or  x.property_done == "False" or  x.property_done == ""  else 1 , axis=1 )
df.drop('property_done', axis=1, inplace=True)

df = df.rename(columns={'property_url': 'url'
                        , 'url': 'n_url'
                        , 'property_create_dt': 'dt_crt'
                        })

# print(df.head)

conn = sqlite3.connect(storeFolder + "articles.db")
cur = conn.cursor()

cur.execute("""
DROP table if exists  temp_url;
""")
conn.commit() 

cur.execute("""
CREATE TABLE temp_url (
    n_url  TEXT,
    url    TEXT,
    dt_crt TEXT,
    done   INTEGER
);""")
conn.commit() 


try:
    df.to_sql('temp_url', conn, if_exists='append', index = False, chunksize = 10000)
    conn.commit()   
except sqlite3.Error as er:
    print("duplicate")

print(cur.execute("select COUNT(*) from temp_url").fetchall())

data = cur.execute('''   
INSERT OR IGNORE INTO url (url,n_url,dt_crt,done)
SELECT url,n_url,dt_crt,done 
FROM temp_url
 ''')
conn.commit() 

cur.execute("""
DROP table if exists temp_url
""")
conn.commit() 

conn.close()