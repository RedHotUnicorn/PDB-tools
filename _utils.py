import logging

logging.basicConfig()
logger = logging.getLogger('PDB_tools_logger')
logger.setLevel(logging.DEBUG)

import os
import configparser
import sqlite3
import subprocess
import markdown
from urlextract import URLExtract
import re
import pandas as pd
from nltk.corpus import stopwords
import time



"""
DEFINE MOST USABLE VARS FOR DB CONNECTION

"""
LAUNCH_FOLDER  = os.path.dirname(__file__)


config = configparser.ConfigParser()
config.read(os.path.join(LAUNCH_FOLDER , '_config.ini'))
logger.debug("Config path: ",os.path.join(LAUNCH_FOLDER , '_config.ini'))


# RESULTS_FOLDER  = os.path.dirname(__file__) + os.sep + "results" + os.sep 

# CSV_NOTION      = r'C:\Users\User\Downloads\notion.csv'
# CSV_NOTION      = config['path']['CSV_NOTION']
DB_ID_NOTION    = config['path']['DB_ID_NOTION']
AUTH_NOTION     = config['path']['AUTH_NOTION']


# VAULT_PATH      = r"C:\MyFiles\PKM\PDB"
VAULT_PATH      = config['path']['VAULT_PATH']
VAULT_CSV_PATH  = VAULT_PATH + os.sep + "CSV" + os.sep 

DB_FILE_NAME    = config['store']['DB_FILE_NAME']
DB_FILE_PATH    = config['store']['DB_FILE_PATH']
DB_CONNECTION   = sqlite3.connect(os.path.join(LAUNCH_FOLDER , DB_FILE_PATH , DB_FILE_NAME))
DB_CURSOR       = DB_CONNECTION.cursor()
DB_ERROR        = sqlite3.Error


# YT_DLP_EXE      = r"C:\Program Files\yt-dlp\yt-dlp.exe"
YT_DLP_EXE      = config['path']['YT_DLP_EXE']
# YT_DLP_FIX_VTT  = r"C:\Program Files\yt-dlp\fix_youtube_vtt.py"
YT_DLP_FIX_VTT  = config['path']['YT_DLP_FIX_VTT']

# YT_DLP_GET_SUBS    = rf'''
#     "{YT_DLP_EXE}" --encoding utf-8 --no-check-certificate --sub-lang "ru,en" --write-auto-sub --write-sub --embed-subs --skip-download -o "test" "{{0}}" 1>nul 
#     && ( (      if exist test.ru.vtt (py "{YT_DLP_FIX_VTT}" test.ru.vtt && echo **###  Subs RU** && echo:  && type test.ru.*.txt && echo:  )) 
#             &   if exist test.en.vtt (py "{YT_DLP_FIX_VTT}" test.en.vtt && echo **###  Subs EN** && echo:  && type test.en.*.txt ) ) 
#     &&  del test.*
# '''.replace('\n','')

# TODO probably i can use https://github.com/bindestriche/srt_fix
YT_DLP_GET_SUBS   = rf'''
    chcp 65001 && 
    "{YT_DLP_EXE}" --no-check-certificate --sub-lang "ru,en" --write-auto-sub --write-sub --embed-subs --skip-download -o "test" "{{0}}" 1>nul 
    && (    (      
                if exist test.ru.vtt (py "{YT_DLP_FIX_VTT}" test.ru.vtt  && echo:  && type test.ru.*.txt && echo: )
            ) 
            &   if exist test.en.vtt (py "{YT_DLP_FIX_VTT}" test.en.vtt  && echo:  && type test.en.*.txt ) 
            &&  del test.*
        ) 
'''.replace('\n','')





URL_REGEXP          = r"https?\:\/\/[a-zA-Z0-9\.\/\?\:@\-_=#]+\.(?:[a-zA-Z]){2,6}(?:[a-zA-Z0-9\.\&\/\?\:@\-_=#])*"
URL_PROP_REGEXP     = r"url::.*"
# URL_STRIKE_REGEXP   = r"~~\s*" + URL_REGEXP + r"\s*~~"
URL_STRIKE_REGEXP   = r"\~\~\s*\[.*\]\(https?\:\/\/[a-zA-Z0-9\.\/\?\:@\-_=#]+\.(?:[a-zA-Z]){2,6}(?:[a-zA-Z0-9\.\&\/\?\:@\-_=#])*\)\s*\~\~"
URL_STRIKE_REGEXP   = r"\~\~\s*\[.*\]\("+ URL_REGEXP +r"\)\s*\~\~"
def run_extracting_YT_subs(YT_URL):
    """
    This functions uses YT_DLP_GET_SUBS as string to be launched with url as params
    
    """
    # TODO Somehow this process when runs print additional chars like "test.ru.vtt.txt" 
    res = subprocess.run(
                            YT_DLP_GET_SUBS.format(YT_URL) 
                            , shell=True
                            , text=True
                            , stdout=subprocess.PIPE
                            , encoding="utf-8") 
    time.sleep(5)
    return res.stdout


def get_Meta_Property_from_MD(path,file,prop):
    ret     = None

    f       = open(   os.path.join(path, file), 'r', encoding="utf-8")
    md      = markdown.Markdown(extensions=['full_yaml_metadata'])
    md.convert(f.read())
    
    if md.Meta !="" and md.Meta!= None:
        if prop in md.Meta and md.Meta[prop] != None:
            m_p = md.Meta[prop]
            if isinstance(m_p, str):
                m_p = [m_p]
            ret = list(filter(lambda x: x is not None, m_p))
    
    return ret



def get_URLs_from_file(path,file):
    """
    to test 
    a = get_URLs_from_file(r'C:\MyFiles\PKM\PDB\1 - 📝  Reference Base','🎥 GTD A guide to Getting Things Done OneStutteringMind.md')
    a = get_URLs_from_file(r'C:\MyFiles\PKM\PDB\0 - 📥  Inbox','🖼️ Writing is thinking.canvas')

    so first we need to find MAIN url of md or canvas
    if we found to we can remove all duplicates in this text
    
    after that we could find all other urls
    """

    text                = open(   os.path.join(path, file), 'r', encoding="utf-8").read()
    extractor           = URLExtract()

    res_url             = {}
    res_url["prop"]     = []  
    res_url["done"]     = [] 
    res_url["located"]  = []  

    prop_url_find       = re.findall(URL_PROP_REGEXP,text)
    if prop_url_find:
        prop_url_search = extractor.find_urls( prop_url_find[0])
        if prop_url_search:
            res_url["prop"].append(prop_url_search[0])

    strike_url_find     = re.findall(URL_STRIKE_REGEXP,text)
    if strike_url_find:
        strike_ur_search = extractor.find_urls( str(strike_url_find))
        if strike_ur_search:
            res_url["done"].extend(strike_ur_search)

    # https://gist.github.com/bgusach/a967e0587d6e01e889fd1d776c5f3729
    # https://stackoverflow.com/a/55889140/5353177
    [text := text.replace(x, '') for x in prop_url_find]
    [text := text.replace(x, '') for x in strike_url_find]

    additional_urls     = extractor.find_urls( text )
    additional_urls     = [k for k in additional_urls if k.startswith('http')]
    additional_urls     = [k for k in additional_urls if not k.startswith('https://todoist.com/showTask')]

    res_url["located"]  = additional_urls

    # return prop_url , additional_urls
    return res_url



def extract_stop_words():
    storeFolder = os.path.join(os.path.dirname(__file__) , "additional files")

    russian_stopwords = stopwords.words("russian")
    f = open(storeFolder + "russian_stopwords.txt", "w", encoding="utf-8")
    f.write('\n'.join(map(str, russian_stopwords)))
    f.close()

    english_stopwords = stopwords.words("english")
    f = open(storeFolder + "renglish_stopwords.txt", "w", encoding="utf-8")
    f.write('\n'.join(map(str, english_stopwords)))
    f.close()


"""
######################################################################
                    TEXT QUERIES FOR SQL
######################################################################
"""

DROP_TBL_SQL        =   """
                        DROP table if exists  {};
                        """
GET_DDL_TBL_SQL     =   """
                        SELECT sql 
                        FROM sqlite_master 
                        WHERE 
                        tbl_name = '{}';
                        """
DUP_EMPTY_TBL_SQL   =   """
                        CREATE TABLE 
                        {} 
                        AS  SELECT * 
                            FROM {}
                        WHERE 0
                        """


"""
######################################################################
                    VIEWS TRANSFORMATIONS
######################################################################
"""
import w3lib.url
import urllib.parse
import requests

REMOVE_PARAMS_ARRAY = [
      'utm_campaign'
    , 'utm_medium'
    , 'utm_source'
    , 'utm_name'
    , 'utm_term'
    , 'utm_content'
]


STRICT_PARAMS_DICT  = {
      "www.youtube.com" :['v', 'list','t']
}

EXCL_REDIR_ARRAY    = [
      "https://consent."
    , "https://www.linkedin.com/signup/cold-join"
    # , "www."
]

def link_expand(link):
    """
    1. get req with redirects
    2. get last redirect after excluding "wrong" redirects.

    Example:
    - https://m.youtube.com/playlist?list=PL_yqdE3j5wTCJxy6J5bqSkCs0KxCWVAVL
    V
    - https://www.youtube.com/playlist?app=desktop&list=PL_yqdE3j5wTCJxy6J5bqSkCs0KxCWVAVL
    V
    - https://consent.youtube.com/ml?continue=https://www.youtube.com/playlist?app%3Ddesktop%26list%3DPL_yqdE3j5wTCJxy6J5bqSkCs0KxCWVAVL%26cbrd%3D1&gl=DE&hl=de&cm=2&pc=yt&src=1
    
    the last one is not nessesary. so we need exclude it
    """
    response = requests.head(link, allow_redirects=True)                                 # https://stackoverflow.com/questions/70560247/bypassing-eu-consent-request
    
    
    tmp_res = [resp.url for resp in response.history if not any(x in resp.url for x in EXCL_REDIR_ARRAY)][-1] if response.history else response.url
    return '' if not isinstance(tmp_res, str) else tmp_res

    """
    TODO: 
    Somehow I need to recognise such transformation... Manual variant works but every time need to fix
    - "https://sql-optimizer.streamlit.app/"
    V		
    - "https://sql-optimizer.streamlit.app/-/login?payload=MTY5ODY5OTM2NXw5YV9KTVl2SXAtTVNya2NrS3U4RlJ3UG0wQlAwQjJ3STdvcGpSZzk2Z2ZVOEc5Z1ROVHF5NWhqaGw1Q2JoZDVnUldFX1VCVTI3TlJuS0ZRZFJyNUthLXFhMVJQMzhlc2sxSThZNXZlendiN3BhR3YzODM5T0RnNXVuYjQ3eXlFN2lZeHI1TXFXRlFRS1k1VjRWejJoa2s2YnhScE9BdU1LUWpZUW9vaDBzOHhucmtvbXB4QUozY1dzeG1EU1hlMWVndkVGcm9uYjhtcnUyTjhJVWRuV0xkb0l3cWxNN1k1VVFkaTdHa2pqTG1LeHVpbUNWYm1ZMDdaZWxlTi1MZW1PellJaGp2dUZNdHBRYzh4ZEdfdHRPei1YenZ5SXE5MmExYm1XVllxZkFCZUVaSWtKV2VCOTQ3b0dwWUQ1bzl1TVR0b1N4N2F1eE5Xci1zUmE0US1XOFRDQ0NXYnNCLXNhV1NlZ1cxX0labGVpVWo0VzlfcHRJVWpIRGNGWW5UeU10Y3hhTXRRYjUyYy1CUmVrMl9kZ0VJZTViVWcwYmlFNzdrZ3kwaTdWNWdOY3JSd3FNWHFuWExKMjI3NG5qR3BpUjFCT1doSWlIdlpEMjNHVlFyd3pzR1V6UTVWbDg3TWNXcDJEYmY1a05lTDRLQ1ZUMnVVMXhmWG9VRjdoQTJFNzJpM0JyaWx4S2N6MVdZd3hoTDdwM1hnQnzhNT077_OAts4Nrn2u0_nBkbm63EQYItY5eel4wryPYg%3D%3D"
    
    """


def base_link_to_gold_link(base_link):
    """
    1. Standartize the curent url
    2. Parse the hostname and query
    3. If the query contains smth from REMOVE_PARAMS_ARRAY (mostly it's form RSS) -- remove it
    4. If the hostname eq to some espeitial rules -- repmve all except params from array

    version right now not used but should be , probably
    """
    version         = '2023-10-29'
    gold_link       = base_link

    try:
        gold_link = gold_link.replace("&amp;", "&")
        gold_link =  link_expand(gold_link)                                             # try_expand      = urlexpander.expand(base_link , use_head=False)                # gold_link = url_normalize(urlexpander.expand(base_link)) 
                                                                                        # if      (   "__CLIENT_ERROR__".lower()          not in try_expand.lower() ) \
                                                                                        #     and (   "__connectionpool_error__".lower()  not in try_expand.lower() ):    # __CLIENT_ERROR__: https://github.com/SMAPPNYU/urlExpander/issues http://t.me\__connectionpool_error__/
                                                                                        #     gold_link   = try_expand                          

        o               = urllib.parse.urlsplit(gold_link)
        o_query         = dict(urllib.parse.parse_qsl(o.query))                         # https://gist.github.com/rokcarl/20b5bf8dd9b1998880b7
        for key in REMOVE_PARAMS_ARRAY:
            o_query.pop(key, None)                                                      # https://stackoverflow.com/a/70785605/5353177

        gold_link = o._replace(query=urllib.parse.urlencode(o_query)).geturl()

        o_hostname      = o.hostname
        if o_hostname in STRICT_PARAMS_DICT:
            params = STRICT_PARAMS_DICT[o_hostname]
            gold_link = w3lib.url.url_query_cleaner(gold_link,params)
    except Exception as e:
        print(gold_link ," ",base_link)
        print(e)
        gold_link = ''

    return gold_link

# import requests
# response = requests.head('https://m.youtube.com/playlist?list=PL_yqdE3j5wTCJxy6J5bqSkCs0KxCWVAVL', allow_redirects=True) # https://stackoverflow.com/questions/70560247/bypassing-eu-consent-request
# for resp in response.history :
#     if "https://consent." not in resp.url:
#         print(resp.status_code, resp.url)
#         # 302 https://m.youtube.com/playlist?list=PL_yqdE3j5wTCJxy6J5bqSkCs0KxCWVAVL
#         # 302 https://www.youtube.com/playlist?app=desktop&list=PL_yqdE3j5wTCJxy6J5bqSkCs0KxCWVAVL
# print(response.url)
# print(response.is_redirect)

