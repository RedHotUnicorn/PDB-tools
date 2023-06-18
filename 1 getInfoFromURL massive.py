import requests
import trafilatura

from bs4 import BeautifulSoup
from urllib.parse import urlsplit
import sqlite3
import argparse
import pandas as pd
import PDButils as u





def tryToLoad(url):
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
                        case "youtube.com":
                                print("test")
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
    
    
        
sql_query = pd.read_sql_query ('''
                               SELECT
                                    url
                                    ,n_url
                               FROM url
                               where url not in (select url
                                                    from articles where  m_length > 0)
                               ''', u.DB_CONNECTION)

df = pd.DataFrame(sql_query, columns = ['url', 'n_url'])

df[['markdown','og_type']] = df.apply(lambda x: tryToLoad(x.url), axis=1, result_type='expand')
print (df)

try:
    df.to_sql('temp_articles', u.DB_CONNECTION, if_exists='append', index = False, chunksize = 10000)
    u.DB_CONNECTION.commit()   
except sqlite3.Error as er:
    print("duplicate")

print(u.DB_CURSOR.execute("select COUNT(*) from temp_articles").fetchall())

data = u.DB_CURSOR.execute('''   
INSERT OR IGNORE INTO articles (url,n_url,markdown,og_type)
SELECT url,n_url,markdown,og_type 
FROM temp_articles
''')
u.DB_CONNECTION.commit() 


u.DB_CURSOR.execute("""
DROP table if exists temp_url
""")
u.DB_CONNECTION.commit() 

u.DB_CONNECTION.close()

# data = (url ,n_url,text,type)
# try:

#     cur.execute("INSERT INTO articles VALUES(?,?,?,?)", data)
#     u.DB_CONNECTION.commit()  
# except sqlite3.Error as er:
#     print("duplicate")
#     print(url)
# u.DB_CONNECTION.close()
