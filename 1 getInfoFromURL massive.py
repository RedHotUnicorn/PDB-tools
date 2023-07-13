import requests
import trafilatura

from bs4 import BeautifulSoup
from urllib.parse import urlsplit
import sqlite3
import argparse
import pandas as pd
import PDButils as u

INPUT_TBL_1     = 'NTN_V_url'
INPUT_TBL_2     = 'content'

OUTPUT_TBL_1    = INPUT_TBL_2
OUTPUT_TMP      = 'temp_articles'
def load_url_text(url):
    text = ""
    type = ""
    try:
        r = requests.head(url, allow_redirects=True)
        if r.status_code == 200:
            if  "application" in r.headers['Content-Type'] or "image" in r.headers['Content-Type']:
                print("that not a text")
            else:
                try:
                    o = urlsplit(url)
                    match o.hostname:
                        case "t.me":
                            url+="?embed=1&mode=tme"  
                        # If an exact match is not confirmed, this last case will be used if provided
                        case _:
                            url = url
                    downloaded = trafilatura.fetch_url(url)

                    soup = BeautifulSoup(downloaded , "lxml")
                    # title = soup.find("meta", property="og:title")
                    # title = title["content"] if title else None

                    # og_description = soup.find("meta", property="og:description")
                    # og_description = og_description["content"] if og_description else None

                    # description = soup.find("meta", property="description")
                    # description = description["content"] if description else None

                    type = soup.find("meta", property="og:type")
                    type = type["content"] if type else None


                    #TODO content-language

                    match o.hostname:
                        case "youtube.com" | 'youtu.be' | "m.youtube.com":
                            text = u.run_extracting_YT_subs(url)
                        case _:
                            text=trafilatura.extract(   downloaded
                                                        ,include_images=True
                                                        ,include_formatting=True
                                                        # this links creates maybe sometimes a lot of links
                                                        , include_links=True
                                                        # ,favor_precision=True
                                                        , include_comments=True
                            )


                except:
                    print("some another error")
    except:
        print("host unreachable") 
    return [text , type]
    
    
        
sql_query = pd.read_sql_query (f"""
                               SELECT
                                    id
                                    ,url
                               FROM {INPUT_TBL_1}
                               where id not in (select id
                                                    from {INPUT_TBL_2} where  m_length > 0)   
                                --limit 100                        
                               """, u.DB_CONNECTION)

df = pd.DataFrame(sql_query, columns = ['id', 'url'])
# print (df)

df[['markdown','og_type']] = df.apply(lambda x: load_url_text(x.url), axis=1, result_type='expand')
# print (df)

u.DB_CURSOR.execute(f"""
                        DROP table if exists {OUTPUT_TMP}
                    """)

try:
    df.to_sql(
                OUTPUT_TMP
                , u.DB_CONNECTION
                , if_exists='append'
                , index = False
                , chunksize = 10000
            )
    u.DB_CONNECTION.commit()   
except sqlite3.Error as er:
    print("duplicate")

# print(u.DB_CURSOR.execute("select COUNT(*) from temp_articles").fetchall())


# TODO this is works not right. Should create rule for update markdown

# TODO should I use files instead of DB markdown?
data = u.DB_CURSOR.execute(f'''   
                                INSERT INTO {OUTPUT_TBL_1} (id,markdown,og_type)
                                SELECT  id,markdown,og_type
                                FROM    {OUTPUT_TMP}
                                WHERE 1
                                        ON CONFLICT(id) 
                                            DO UPDATE 
                                            SET markdown =   excluded.markdown
                                            ,og_type =   excluded.og_type
                            ''')
u.DB_CONNECTION.commit() 

u.DB_CURSOR.execute(f"""
                        DROP table if exists {OUTPUT_TMP}
                    """)
u.DB_CONNECTION.commit() 
u.DB_CONNECTION.close()
