import pandas as pd
import sqlite3
import PDButils as u


OUTPUT_TBL  = 'NTN_url'
TEMP_TBL    = 'temp_url'

"""
1. Load data from csv
2. Calculate shurely property done 
3. Rename columns for format of table
"""

df          = pd.read_csv(u.CSV_NOTION
                          , usecols = ['property_url','url','property_create_dt','property_done']
                          )
df['done']  = df.apply(lambda x: 0 if x.property_done == False or  x.property_done == "False" or  x.property_done == ""  else 1 
                       , axis=1 )
df.drop(    'property_done'
            , axis=1
            , inplace=True
        )

df = df.rename(columns={    'property_url'          : 'url'
                            , 'url'                 : 'n_url'
                            , 'property_create_dt'  : 'dt_crt'
                        })


"""
1. Drop temp table  in some case 
2. Create new one with exact structure as target
3. Put data into df to temp table 
"""

u.DB_CURSOR.execute(f"""
                    DROP table if exists  {TEMP_TBL};
                    """)
u.DB_CONNECTION.commit() 

u.DB_CURSOR.execute(f"""
                    CREATE TABLE {TEMP_TBL} (
                        n_url  TEXT,
                        url    TEXT,
                        dt_crt TEXT,
                        done   INTEGER
                    );""")
u.DB_CONNECTION.commit() 

try:
    df.to_sql(  TEMP_TBL
                , u.DB_CONNECTION
                , if_exists ='append'
                , index     = False
                , chunksize = 10000
                , method='multi')
    u.DB_CONNECTION.commit()   
except u.DB_ERROR as er:
    print("duplicate")


"""
1. Finaly insert results from temp table to output
2. Drop temp table
"""

data = u.DB_CURSOR.execute(f'''   
                            INSERT OR IGNORE INTO {OUTPUT_TBL} (url,n_url,dt_crt,done)
                            SELECT url,n_url,dt_crt,done 
                            FROM {TEMP_TBL} 
                            ''')
u.DB_CONNECTION.commit() 

u.DB_CURSOR.execute(f"""
                    DROP table if exists {TEMP_TBL} 
                    """)
u.DB_CONNECTION.commit() 

u.DB_CONNECTION.close()