import logging

logging.basicConfig()
logger = logging.getLogger('PDB_tools_logger')
logger.setLevel(logging.DEBUG)

import  os
import  configparser
import  sqlite3
import  subprocess
import  markdown
from    urlextract import URLExtract
import  re
import  pandas as pd
from    nltk.corpus import stopwords
import  time
from difflib import SequenceMatcher

import  trafilatura
from    bs4 import BeautifulSoup
from    pathlib import Path
from    datetime import datetime
import  hashlib
import  uuid
import  frontmatter
from yaml import CSafeDumper as SafeDumper


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
DWN_VAULT_PATH  = config['path']['DWN_VAULT_PATH']
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

ADD_PARAMS_DICT  = {
      "t.me" : {"embed":1 , "mode": "tme"}
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

        o_hostname          = o.hostname
        if o_hostname in STRICT_PARAMS_DICT:
            params          = STRICT_PARAMS_DICT[o_hostname]
            gold_link       = w3lib.url.url_query_cleaner(gold_link,params)
        if o_hostname in ADD_PARAMS_DICT:
            params_to_add   = ADD_PARAMS_DICT[o_hostname]
            gold_link       = w3lib.url.add_or_replace_parameters(gold_link,params_to_add)
        
    except Exception as e:
        print(gold_link ," ",base_link)
        print(e)
        gold_link = ''

    return gold_link

# import requests
# response = requests.head('https://m.youtube.com/playlist?list=PL_yqdE3j5wTCJxy6J5bqSkCs0KxCWVAVL', allow_redirects=True) # https://stackoverflow.com/questions/70560247/bypassing-eu-consent-request
# response = requests.head('''https://www.linkedin.com/posts/aurelienvautier_businessintelligence-dataanalytics-dashboard-activity-7097459717383311360-db1X''', allow_redirects=True) # https://stackoverflow.com/questions/70560247/bypassing-eu-consent-request
# # response = requests.head('''https://sql-optimizer.streamlit.app/''', allow_redirects=True) # https://stackoverflow.com/questions/70560247/bypassing-eu-consent-request
# # response = requests.head('''https://bit.ly/3dV6cFr''', allow_redirects=True) # https://stackoverflow.com/questions/70560247/bypassing-eu-consent-request


# for resp in response.history :
#     # if "https://consent." not in resp.url:
#         # print(resp.status_code, resp.url)
#     print(resp.status_code, resp.url)
#     print('-'*200)
#         # 302 https://m.youtube.com/playlist?list=PL_yqdE3j5wTCJxy6J5bqSkCs0KxCWVAVL
#         # 302 https://www.youtube.com/playlist?app=desktop&list=PL_yqdE3j5wTCJxy6J5bqSkCs0KxCWVAVL
# print(response.url)
# print(response.is_redirect)

# text1 = 'https://m.youtube.com/playlist?list=PL_yqdE3j5wTCJxy6J5bqSkCs0KxCWVAVL'
# text2 = 'https://www.youtube.com/playlist?app=desktop&list=PL_yqdE3j5wTCJxy6J5bqSkCs0KxCWVAVL'
# print(SequenceMatcher(None, text1, text2).ratio())

# text1 = 'https://www.youtube.com/playlist?app=desktop&list=PL_yqdE3j5wTCJxy6J5bqSkCs0KxCWVAVL'
# text2 = 'https://consent.youtube.com/ml?continue=https://www.youtube.com/playlist?app%3Ddesktop%26list%3DPL_yqdE3j5wTCJxy6J5bqSkCs0KxCWVAVL%26cbrd%3D1&gl=DE&hl=de&cm=2&pc=yt&src=1'
# print(SequenceMatcher(None, text1, text2).ratio())

# text1 = 'https://sql-optimizer.streamlit.app/'
# text2 = 'https://share.streamlit.io/-/auth/app?redirect_uri=https%3A%2F%2Fsql-optimizer.streamlit.app%2F'
# print(SequenceMatcher(None, text1, text2).ratio())

# text1 = 'https://share.streamlit.io/-/auth/app?redirect_uri=https%3A%2F%2Fsql-optimizer.streamlit.app%2F'
# text2 = 'https://sql-optimizer.streamlit.app/-/login?payload=MTcwMjMyNTkxM3xkYzMycUFQUC16V3p6ZmZENEJWTnp6VVR5S1RrTTliZ0ZVS2tvUEhzUVRUMG1TSlhqWnN6OU1qdmFENDBpWUJ6ZWxHTURjUFFwVnJQaUZMcFlqRnNmSDhiZmpWd09aYks5MjBPVks3cGtIbjR2U21TMWtzTXI5dDZ6NS1saElEcm9zY0pkX3hBN2NoVGJZMUdFd1dRX1pmX2VwbE1qQlJaOTA1enJ0R1hMQ3VHUE9JOTUwWi1veTFLNGdYeHlSWF9yazVpLTBBTk9BYTZxTW9GU0lNMjVqYkRPT0FtZk1HNzlHYUQ1czZ0N3ZKT1pUaFdVaXl0MDRpcU84ajh6QzlPOG0wVWY4T1QwSklTVmg4WE04M0N3bFJEdXhBMmdocnYxclhlb2xCRUhFc2x3bVNJZ2h2ZGRfb3VIN0V2WU1zZjUyUU91N3o4dWplbVEwakNXYi00VlpKdFdHLWczQnBhUjBXcUxlSmlQdjh5Q0taQ3d3ZlRNeHRNZzFkS0lWNFpsWUZQTXFkVGF4eFBqRFl3VDBJQUVZbTc1S3F6QXN0SS1TRm02c2t0RzNtNE9FeE1vMVVPVXJudmdrZDZzVnNueXd5dXRGemJsYWN5SFNXN2xub0hkdnRvd0hZbGtzRjk2SzBVOXhXRUNpaGcyRWMzZzdOc1VlRk9LT044SDdSSG9JdlpsMFFGeUUzeTlpRFVXTFF2U0t2OXx6xAddRJr5D34xPszvGcHOu7Dy_64N-h9R04W_vff92Q%3D%3D'
# print(SequenceMatcher(None, text1, text2).ratio())


# text1 = 'https://www.linkedin.com/posts/aurelienvautier_businessintelligence-dataanalytics-dashboard-activity-7097459717383311360-db1X'
# text2 = 'https://www.linkedin.com/signup/cold-join?session_redirect=https%3A%2F%2Fwww.linkedin.com%2Ffeed%2Fupdate%2Furn%3Ali%3Aactivity%3A7097459717383311360'
# print(SequenceMatcher(None, text1, text2).ratio())



text1 = 'test test test test remove'
text2 = 'append test test test test append '
print(SequenceMatcher(None, text1, text2).ratio())
print(SequenceMatcher(None, text2, text1).ratio())

"""
######################################################################
                    WORK WITH MD FILES
######################################################################
"""

def download_title_and_content(url):
    # TODO in v1 code I had the IF 
    # if  "application" in r.headers['Content-Type'] or "image" in r.headers['Content-Type']:
    """
    1. Fetch by trafilatura
    2. BS for deleting attributes of pre, code, li
    3. additional replacements bcs trafilatura can't catch some code blocks
    """
    try:
        downloaded_bs = BeautifulSoup(    trafilatura.fetch_url(url)
                                        , features="html.parser")
        title_all = [x.get_text() for x in downloaded_bs.find_all('title')]

        title = title_all[0] if title_all  else None


        [tag.attrs.clear() for tag in downloaded_bs.find_all(['pre','code',"li"])]
        cleaned_html = downloaded_bs.prettify()

        sent=trafilatura.extract(
            (
                cleaned_html
                .replace("</code></pre>", "</code>```</pre>")
                .replace("<pre><code", "<pre>```<code")
                .replace("<li>", "<li>\n")
            )
            #, output_format='xml'
            # ,include_images=True
            ,include_formatting=True
            , include_links=True
            # ,favor_precision=True
            ,include_comments=True
        ).replace('```', "\n```\n")
    except:
        sent = ''
        title = ''

    return [ title , sent ]




def save_to_file(file_name,cnt_str='',mt_dict=None,folder_path=DWN_VAULT_PATH):
    ret          = frontmatter.Post(content='')
    ret.content  = cnt_str
    ret.metadata = mt_dict
    # print(mt_dict)
    # print(ret.metadata)

    bool = True
    try:

        with open(os.path.join(folder_path,file_name), "w", encoding="utf-8") as f:
            f.write(frontmatter.dumps(ret , sort_keys=False))
            # https://github.com/eyeseast/python-frontmatter/issues/26#issuecomment-799024484
    except:
        bool = False
        # TODO warning
    return bool

def get_valid_filename(str):
    return "".join( x for x in str if (x.isalnum() or x in "._- "))

def first_try_url(url):
    r = requests.head(url, allow_redirects=True)
    return [r.status_code, r.headers['Content-Type']]















def generate_hash(file_or_str):
    
    if isinstance(file_or_str, str):
        s = file_or_str
    elif hasattr(file_or_str, "read"): 
        s = file_or_str.read()
    return uuid.uuid5(uuid.NAMESPACE_DNS, s).hex

def get_yaml_meta_from_file(fd):
    ret     = None
    if hasattr(fd, "read"): 
        f = fd.read()
    else:
        with open(fd, "r", encoding="utf-8") as f:
            f = f.read()
    md      = markdown.Markdown(extensions=['full_yaml_metadata'])
    md.convert(f)
    
    if md.Meta !="" and md.Meta!= None:
        ret = md.Meta
    # ret = list(filter(lambda x: x is not None, ret))
    return ret


def get_vault_files_as_df(folder_path=DWN_VAULT_PATH):
    # https://stackoverflow.com/questions/59197529/get-information-about-files-in-a-directory-and-print-in-a-table
    directory = Path(folder_path)
    paths = []
    filename = []
    size = []
    hashes = []
    modified = []
    yaml_meta = []
    files           = list(directory.glob('**/*.md'))

    for file in files:
        paths.append(file.parents[0])
        filename.append(file.parts[-1])
        size.append(file.stat().st_size)
        modified.append(datetime.fromtimestamp(file.stat().st_mtime))
        with open(file, encoding="utf-8") as f:        
            hashes.append(generate_hash(f))
        yaml_meta.append(get_yaml_meta_from_file(os.path.join(file.parents[0],file.parts[-1]) ))

    columns         = ['f_path', 'f_Name'  , 'f_size'   ,'f_lm', 'f_ash', 'f_yaml'    ]
    data            = [paths ,  filename    , size          , modified      , hashes    , yaml_meta ]
    df              = pd.DataFrame(dict(zip(columns, data)))
    df              = df.join(pd.json_normalize(df['YAML']))
    return df

















# pd.options.display.width = 0
# pd.options.display.width = 600
# pd.set_option('display.max_columns', None)
# pd.set_option('display.expand_frame_repr', False)
# pd.set_option('max_colwidth', None)