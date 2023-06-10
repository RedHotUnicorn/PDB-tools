import requests
import trafilatura
import os
from bs4 import BeautifulSoup
from urllib.parse import urlsplit
import sqlite3
import argparse
import pandas as pd


storeFolder = os.path.dirname(__file__) + os.sep + "results" + os.sep 

# url = 'http://www.virginaustralia.com/au/en/bookings/flights/make-a-booking/'
# url = 'https://arxiv.org/pdf/1709.08546.pdf'
# url = 'https://static.wixstatic.com/media/b87edf_e3ba99794af542e394b7a9895bb7c8a9~mv2.png/v1/fit/w_1000%2Ch_888%2Cal_c/file.png'

# url = 'https://blog.davidsha.me/how-to-automatically-update-n8n-python/'
# url = 'https://habr.com/en/company/dododev/blog/722354/'
# url='https://community.n8n.io/t/extract-first-column-of-an-html-table/7302'
# url='https://meduza.io/feature/2023/03/16/zhitelyam-rossiyskih-regionov-nachali-prisylat-povestki-v-voenkomat-dlya-utochneniya-dannyh-vse-vtoraya-volna-mobilizatsii-po-tihomu-nachalas-i-mozhno-li-prosto-proignorirovat-povestku'
# url='https://docs.n8n.io/choose-n8n/desktop-app/'
# url='https://www.youtube.com/watch?v=9OUVU-obKJw&ab_channel=SHIROKOVLITE'

# first lets try to understand is it a some pdf or image

# parser = argparse.ArgumentParser()
# parser.add_argument('url')
# parser.add_argument('n_url')
# args = parser.parse_args()

# url = args.url
# n_url = args.n_url


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


                    text=trafilatura.extract(downloaded
                    ,include_images=True
                    ,include_formatting=True
                    # this links creates maybe sometimes a lot of links
                    , include_links=True
                    # ,favor_precision=True
                    , include_comments=True
                    )
                    # print(text)


                except:
                    print("some another error")
    except:
        print("host unreachable") 
    return [text , type]
    
    
con = sqlite3.connect(storeFolder + "articles.db")
cur = con.cursor()


         
sql_query = pd.read_sql_query ('''
                               SELECT
                                    url
                                    ,n_url
                               FROM url
                               where url not in (select url
                                                    from articles)
                               limit 15
                               ''', con)

df = pd.DataFrame(sql_query, columns = ['url', 'n_url'])

df[['markdown','og_type']] = df.apply(lambda x: tryToLoad(x.url), axis=1, result_type='expand')
print (df)

try:
    df.to_sql('temp_articles', con, if_exists='append', index = False, chunksize = 10000)
    con.commit()   
except sqlite3.Error as er:
    print("duplicate")

print(cur.execute("select COUNT(*) from temp_articles").fetchall())

data = cur.execute('''   
INSERT OR IGNORE INTO articles (url,n_url,markdown,og_type)
SELECT url,n_url,markdown,og_type 
FROM temp_articles
''')
con.commit() 


cur.execute("""
DROP table if exists temp_url
""")
con.commit() 

con.close()

# data = (url ,n_url,text,type)
# try:

#     cur.execute("INSERT INTO articles VALUES(?,?,?,?)", data)
#     con.commit()  
# except sqlite3.Error as er:
#     print("duplicate")
#     print(url)
# con.close()
