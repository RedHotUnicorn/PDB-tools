import pandas as pd
import sqlite3
import _utils as u
from _utils import os as os

CSV_FILE_NAME   = u.config['in']['CSV_FILE_NAME']
CSV_FILE_PATH   = u.config['in']['CSV_FILE_PATH']
CSV             = os.path.join(u.PROJECT_FOLDER,CSV_FILE_PATH,CSV_FILE_NAME)

OUT_TBL         = u.config['DB.in_extract_resources_base_url']['OUT_TBL_NAME']
TMP_TBL         = u.config['DB.in_extract_resources_base_url']['TMP_TBL_NAME']

"""
1. Load data from csv
2. Calculate shurely property done 
3. Rename columns for format of table
"""

df          = pd.read_csv(  CSV
                          , usecols = ['property_url','url','property_create_dt','property_done']
                          )
df['done']  = df.apply(
                       lambda x: 0  if      x.property_done == False 
                                        or  x.property_done == "False" 
                                        or  x.property_done == "FALSE" 
                                        or  x.property_done == ""  
                                    else 1 
                       , axis=1 )
df.drop(    'property_done'
            , axis=1
            , inplace=True
        )

df = df.rename(columns={    'property_url'          : 'base_link'
                            , 'url'                 : 'n_url'
                            , 'property_create_dt'  : 'dt_crt'
                        })

df['gold_url'] = df.apply(lambda x: u.base_link_to_gold_link(x.base_link) , axis=1)

"""
1. Drop temp table  in some case 
2. Create new one with exact structure as target
3. Put data into df to temp table 
"""

u.DB_CURSOR.execute(u.DROP_TBL_SQL.format(TMP_TBL))
u.DB_CONNECTION.commit() 

# u.DB_CURSOR.execute(u.DUP_EMPTY_TBL_SQL.format(TMP_TBL,OUT_TBL))
# u.DB_CONNECTION.commit() 

try:
    df.to_sql(  TMP_TBL
                , u.DB_CONNECTION
                , if_exists ='append'
                , index     = False
                , chunksize = 10000
                , method='multi')
    u.DB_CONNECTION.commit()   
except u.DB_ERROR as er:
    print("duplicate")
    print(er)


# """
# 1. Finaly insert results from temp table to output
# 2. Drop temp table
# """

# data = u.DB_CURSOR.execute(f'''   
#                             INSERT OR IGNORE INTO {OUTPUT_TBL} (url,n_url,dt_crt,done)
#                             SELECT url,n_url,dt_crt,done 
#                             FROM {TEMP_TBL} 
#                             ''')
# u.DB_CONNECTION.commit() 

# u.DB_CURSOR.execute(f"""
#                     DROP table if exists {TEMP_TBL} 
#                     """)
# u.DB_CONNECTION.commit() 

# u.DB_CONNECTION.close()