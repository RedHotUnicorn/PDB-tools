import os
import pandas as pd

import PDButils as u

OUTPUT_TBL  = 'OBS_url'
TEMP_TBL    = 'temp_OBS_url'

df = pd.DataFrame()

for root, dirs, files in os.walk(u.VAULT_CSV_PATH):
    for file in files:
        if file.endswith(".csv"):
            # print(os.path.join(root, file))
            tmp  = pd.read_csv(os.path.join(root, file)
                                , usecols =['URL']
                                , sep=';'
                                )
            tmp = tmp.rename(columns={'URL': 'url'})
            tmp['type'] = 'csv'
            tmp['file'] = file
            
            # df = df.concat(tmp, ignore_index = True)
            df = pd.concat((df, tmp), axis = 0)

df_csv = df


df = pd.DataFrame(columns=['url','type','file'])

for root, dirs, files in os.walk(u.VAULT_PATH):
    for file in files:
        if file.endswith((".md",".canvas")) and not(file.endswith(".excalidraw.md")):
            urls_tpl = u.get_URLs_from_file(root,file)
            
            if urls_tpl[0]:
                tmp = pd.DataFrame(data=[[urls_tpl[0]]] ,columns=['url'])
                tmp['type'] = 'prop'
                tmp['file'] = file
                # df = df.concat(tmp, ignore_index = True)
                df = pd.concat((df, tmp), axis = 0)
            if urls_tpl[1]:
                tmp = pd.DataFrame(data=urls_tpl[1]     ,columns=['url'])
                tmp['type'] = 'text'
                tmp['file'] = file
                # df = df.concat(tmp, ignore_index = True)
                df = pd.concat((df, tmp), axis = 0)

df_md = df

df = pd.concat((df_md, df_csv), axis = 0)



"""
code duplicate....
"""

u.DB_CURSOR.execute(f"""
                    DROP table if exists  {TEMP_TBL};
                    """)
u.DB_CONNECTION.commit() 

u.DB_CURSOR.execute(f"""
                    CREATE TABLE {TEMP_TBL} (
                        url  TEXT,
                        type TEXT,
                        file TEXT
                    );""")
u.DB_CONNECTION.commit() 


try:
    df.to_sql(
                TEMP_TBL
                , u.DB_CONNECTION
                , if_exists='append'
                , index = False
                , chunksize = 10000
                , method='multi'
            )
    u.DB_CONNECTION.commit()  
except u.DB_ERROR as er:
    print("duplicate")

u.DB_CURSOR.execute(f'''   
                            INSERT OR IGNORE INTO {OUTPUT_TBL} (url,type,file)
                            SELECT url,type,file
                            FROM {TEMP_TBL} 
                            ''')
u.DB_CONNECTION.commit() 

u.DB_CURSOR.execute(f"""
                    DROP table if exists {TEMP_TBL} 
                    """)
u.DB_CONNECTION.commit() 

u.DB_CONNECTION.close()