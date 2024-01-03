import logging
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
from    difflib import SequenceMatcher

import  trafilatura
from    bs4 import BeautifulSoup
from    pathlib import Path
import  datetime
import  hashlib
import  uuid
import  frontmatter
from    yaml import CSafeDumper as SafeDumper
import  yt_dlp


def get_valid_filename(str):
    return "".join( x for x in str if (x.isalnum() or x in "._- "))


PROJECT_FOLDER  = next(p for p in Path(__file__).parents    if  "PDB-tools" in p.name 
                                                        and len(list(p.glob('_config.ini'))) 
                                                        and len(list(p.glob('readme.md'))) 
                                                        and len(list(p.glob('.gitignore'))) 
                   )

IN_FOLDER       = PROJECT_FOLDER / 'in'
TMP_FOLDER      = PROJECT_FOLDER / 'tmp'
LOG_FOLDER      = TMP_FOLDER     / 'logs'
OUT_FOLDER      = PROJECT_FOLDER / 'out'


logging         .basicConfig(filename=LOG_FOLDER / get_valid_filename(str(str(datetime.datetime.now())+'.log')) ,encoding='utf8' )
logger          = logging.getLogger('PDB-tools')
logger          .setLevel(logging.DEBUG)


if not PROJECT_FOLDER.exists():
    logger      .error("Folder PROJECT is not exitst:")



config          = configparser.ConfigParser()
config          .read(PROJECT_FOLDER / '_config.ini')
logger          .debug(f"Config path: {PROJECT_FOLDER / '_config.ini'}")

if not IN_FOLDER.exists():
    logger      .error("Folder IN  is not exitst: ")
if not TMP_FOLDER.exists():
    logger      .error("Folder TMP is not exitst: ")
if not OUT_FOLDER.exists():
    logger      .error("Folder OUT is not exitst: ")
if not LOG_FOLDER.exists():
    logger      .error("Folder LOG is not exitst: ")



# VAULT_PATH      = r"C:\MyFiles\PKM\PDB"
VAULT_PATH      = config['path']['VAULT_PATH']
DWN_VAULT_PATH  = config['path']['DWN_VAULT_PATH']
VAULT_CSV_PATH  = VAULT_PATH + os.sep + "CSV" + os.sep 

# DB_FILE_NAME    = config['store']['DB_FILE_NAME']
# DB_FILE_PATH    = config['store']['DB_FILE_PATH']
# DB_CONNECTION   = sqlite3.connect(os.path.join(PROJECT_FOLDER , DB_FILE_PATH , DB_FILE_NAME))
# DB_CURSOR       = DB_CONNECTION.cursor()
# DB_ERROR        = sqlite3.Error


# YT_DLP_EXE      = r"C:\Program Files\yt-dlp\yt-dlp.exe"
# YT_DLP_EXE      = config['path']['YT_DLP_EXE']
# YT_DLP_FIX_VTT  = r"C:\Program Files\yt-dlp\fix_youtube_vtt.py"
# YT_DLP_FIX_VTT  = config['path']['YT_DLP_FIX_VTT']

# YT_DLP_GET_SUBS    = rf'''
#     "{YT_DLP_EXE}" --encoding utf-8 --no-check-certificate --sub-lang "ru,en" --write-auto-sub --write-sub --embed-subs --skip-download -o "test" "{{0}}" 1>nul 
#     && ( (      if exist test.ru.vtt (py "{YT_DLP_FIX_VTT}" test.ru.vtt && echo **###  Subs RU** && echo:  && type test.ru.*.txt && echo:  )) 
#             &   if exist test.en.vtt (py "{YT_DLP_FIX_VTT}" test.en.vtt && echo **###  Subs EN** && echo:  && type test.en.*.txt ) ) 
#     &&  del test.*
# '''.replace('\n','')

# # probably i can use https://github.com/bindestriche/srt_fix
# YT_DLP_GET_SUBS   = rf'''
#     chcp 65001 && 
#     "{YT_DLP_EXE}" --no-check-certificate --sub-lang "ru,en" --write-auto-sub --write-sub --embed-subs --skip-download -o "test" "{{0}}" 1>nul 
#     && (    (      
#                 if exist test.ru.vtt (py "{YT_DLP_FIX_VTT}" test.ru.vtt  && echo:  && type test.ru.*.txt && echo: )
#             ) 
#             &   if exist test.en.vtt (py "{YT_DLP_FIX_VTT}" test.en.vtt  && echo:  && type test.en.*.txt ) 
#             &&  del test.*
#         ) 
# '''.replace('\n','')





URL_REGEXP          = r"https?\:\/\/[a-zA-Z0-9\.\/\?\:@\-_=#]+\.(?:[a-zA-Z]){2,6}(?:[a-zA-Z0-9\.\&\/\?\:@\-_=#])*"
URL_PROP_REGEXP     = r"url::.*"
# URL_STRIKE_REGEXP   = r"~~\s*" + URL_REGEXP + r"\s*~~"
URL_STRIKE_REGEXP   = r"\~\~\s*\[.*\]\(https?\:\/\/[a-zA-Z0-9\.\/\?\:@\-_=#]+\.(?:[a-zA-Z]){2,6}(?:[a-zA-Z0-9\.\&\/\?\:@\-_=#])*\)\s*\~\~"
URL_STRIKE_REGEXP   = r"\~\~\s*\[.*\]\("+ URL_REGEXP +r"\)\s*\~\~"



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
      , "www.reddit.com" : {"rdt":0 }
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
    response = requests.head(link, allow_redirects=True,verify=False)                                 # https://stackoverflow.com/questions/70560247/bypassing-eu-consent-request
    
    
    tmp_res = [resp.url for resp in response.history + [response] if not any(x in resp.url for x in EXCL_REDIR_ARRAY)][-1] if response.history else response.url
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
        gold_link       = gold_link.replace("&amp;", "&")

        o               = urllib.parse.urlsplit(gold_link)
        gold_link       = o._replace(  scheme=o.scheme if o.scheme else "https"                 
                                     , netloc=o.netloc if o.netloc else o.path
                                     , path  ="" if o.path and not o.netloc and not o.scheme  else o.path
                                    ).geturl()                                          # https://stackoverflow.com/a/61859560/5353177


        gold_link       =  link_expand(gold_link)                                       # try_expand      = urlexpander.expand(base_link , use_head=False)                # gold_link = url_normalize(urlexpander.expand(base_link)) 
                                                                                        # if      (   "__CLIENT_ERROR__".lower()          not in try_expand.lower() ) \
                                                                                        #     and (   "__connectionpool_error__".lower()  not in try_expand.lower() ):    # __CLIENT_ERROR__: https://github.com/SMAPPNYU/urlExpander/issues http://t.me\__connectionpool_error__/
                                                                                        #     gold_link   = try_expand                          

        o               = urllib.parse.urlsplit(gold_link)
        o_query         = dict(urllib.parse.parse_qsl(o.query))                         # https://gist.github.com/rokcarl/20b5bf8dd9b1998880b7
        for key in REMOVE_PARAMS_ARRAY:
            o_query.pop(key, None)     
                                                             # https://stackoverflow.com/a/70785605/5353177

        gold_link = o._replace(query=urllib.parse.urlencode(o_query)
                               ,scheme=o.scheme if o.scheme == '' else "https"
                               ).geturl()

        o_hostname          = o.hostname
        # if gold_link.scheme == '':
        #      gold_link.scheme == 'https'
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

def get_hostname(link):
    return urllib.parse.urlsplit(link).hostname



def fuzzy_search():
    text1 = 'test test test test remove'
    text2 = 'append test test test test append '
    print(SequenceMatcher(None, text1, text2).ratio())
    print(SequenceMatcher(None, text2, text1).ratio())
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


"""
######################################################################
                    WORK WITH MD FILES
######################################################################
"""

def download_article_title_and_content(url):
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
        cleaned_html = str(downloaded_bs)

        sent=trafilatura.extract(
            (
                cleaned_html
                .replace("</pre>", "```</pre>")
                .replace("<pre>", "<pre>```")
                # .replace("<li>", "<li>\n")
            )
            #, output_format='xml'
            # ,include_images=True
            ,include_formatting=True
            , include_links=True
            # ,favor_precision=True
            ,include_comments=True
        ).replace('```', "\n```\n")

        sent = re.sub(r"([\s^])(\#[^\s#]+)", r"\1\\\2", sent)
    except:
        sent = None
        title = None
        logger      .warning(f"download_article_title_and_content: Something wrong with URL: {url}")

    return [ title , sent ]

def tsv_to_md(file_path , url) -> str:
    # TODO what if url whil contain &t= as parameter? 
    ret = ''
       
    tsv                 = pd                .read_csv(file_path, sep='\t')
    tsv                 .dropna(inplace=True)
    tsv['text_len']     = tsv['text']       .apply(lambda x :len(str(x)))
    tsv['start_sec']    = tsv['start']      .apply(lambda x :x/1000)

    groups = []
    group = 0
    cumsum = 0
    for n in tsv["text_len"]:
        if cumsum >= 1000:
            cumsum = 0
            group = group + 1
        cumsum = cumsum + n
        groups.append(group)

    # print(groups)

    new                  =  ( tsv           .groupby(groups)
                                            .agg({  'text'      :' '.join
                                                  , 'start_sec' : lambda x: x.min().round().astype(int)})
                            )

    for index, row in new.iterrows():
        ret += f' - ~~[▶]({url}&t={row["start_sec"]})~~  {row["text"]} \n'


    return ret

def download_youtube_audio(url,folder_of_files):
    video_path_local_list = []

    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        "paths" : dict(home = str(folder_of_files)) ,
        'outtmpl': '%(id)s.%(ext)s',
        # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
        'postprocessors': [{  # Extract audio using ffmpeg
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download(url)
        list_video_info = [ydl.extract_info(url, download=False)]

    for video_info in list_video_info:
        video_path_local_list.append(Path(f"{video_info['id']}.wav"))

    for video_path_local in video_path_local_list:
        if video_path_local.suffix == ".mp4":
            video_path_local = video_path_local.with_suffix(".wav")
            result  = subprocess.run(["ffmpeg", "-i", str(video_path_local.with_suffix(".mp4")), "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", str(video_path_local)])




def download_youtube_title_and_content(  url
                                        ,sub_ext            = 'vtt'
                                        ,sub_table_ext      = 'tsv'
                                        ,langs              = ["en","ru"]
                                      ):

    try:
        directory       = TMP_FOLDER / 'download_youtube_title_and_content'
        hash_word       = generate_hash(url)
        files           = list(directory.glob(hash_word+'*'))



        file_tmpl = hash_word
        # langs = ["en","ru"]

        files = []
        for l in langs:
            files.append(dict(    _in  = file_tmpl + '.'+ l + '.' + sub_ext 
                                ,_out  = file_tmpl + '.'+ l + '.' + sub_table_ext 
                                ,_lang = l   ))


        ydl_opts = {
            "subtitleslangs": langs,
            'writeautomaticsub': True,
            "writesub":  True ,
            "embedsubs": True,
            'writedescription': True,
            'subtitlesformat': sub_ext,
            'skip_download': True,
            'paths' : dict(home = str(directory))  ,
            'outtmpl': file_tmpl
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(url)
            info_dict = ydl.extract_info(url, download=False)
            
            video_title = info_dict.get('title', None)
            # TODO maybe we can avoid extracting to the file by _write_subtitles(self, info_dict, filename) 
            # and write subs to variable...
            # https://stackoverflow.com/questions/63916090/extract-the-title-of-a-youtube-video-python
            su          = info_dict.get('requested_subtitles', None)
            if su == None:
                download_youtube_audio(url,IN_FOLDER / 'audio')
            video_lang  = info_dict.get('language', None)

        # print(video_title)
        # print(su)
        
        # sort by prefered lang
        files =  sorted(files, key=lambda x: (x['_lang'] == video_lang),reverse=True)
        # print(files)
            
        sent =''
        print()
        with open(list(directory.glob(hash_word+'*.description'))[0],'r',encoding='utf8') as f:
            sent +='# Description \n'
            sent += f.read()
            sent +='\n'

        for f in files:
            if (directory / f['_in']).is_file():
                with (directory / f['_out']).open('w',encoding='utf8') as fl:
                    fl.write('start\tend\ttext\n')
                    fl.write(fix_youtube_vtt( str(directory / f['_in']) )  )
                    sent+='# '+ f['_lang'] + '\n'
                    sent += tsv_to_md(str(directory / f['_out'])  ,url )

                

        # with open(folder_of_files + get_valid_filename(video_title)+'.md','w',encoding='utf8') as fl:
        #      fl.write(sent)


        files           = directory.glob(hash_word+'*')
        for f in files:
            f.unlink()
    except:
        video_title = None
        sent = None
        logger      .warning(f"download_youtube_title_and_content: Something wrong with URL: {url}")
    

    return [video_title , sent]

def try_download(link):
    print(link)
    array = [None,None]
    try:
        match get_hostname(link):
            case "youtube.com" | 'youtu.be' | "www.youtube.com":
                array = download_youtube_title_and_content(link)    
            case _:
                array = download_article_title_and_content(link)
    except Exception as e:
        print('-'*20 + 'ERROR' + '-'*75)
        print(link)

        print('-'*100)

    
    return array

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


def first_try_url(url):
    try:
        r = requests.head(url, allow_redirects=True , verify=False)
        status_code = r.status_code if r.status_code else -1
    except:
        status_code = -1
    try:
        headers_ct = r.headers['Content-Type'] if r.headers and r.headers['Content-Type'] else None
    except:
        headers_ct = None
    return [status_code, headers_ct]















def generate_hash(file_or_str):
    s = ''
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
        modified.append(datetime.datetime.fromtimestamp(file.stat().st_mtime))
        with open(file, encoding="utf-8") as f:        
            hashes.append(generate_hash(f))
        yaml_meta.append(get_yaml_meta_from_file(os.path.join(file.parents[0],file.parts[-1]) ))

    columns         = ['f_path', 'f_Name'  , 'f_size'   ,'f_lm', 'f_hash', 'f_yaml'    ]
    data            = [paths ,  filename    , size          , modified      , hashes    , yaml_meta ]
    df              = pd.DataFrame(dict(zip(columns, data)))
    df              = df.join(pd.json_normalize(df['f_yaml']))
    # in case if vault is empty
    df['gold_link'] = df.get('gold_link', '')    
    return df


def getdate():
    return datetime.date.today()















# pd.options.display.width = 0
# pd.options.display.width = 600
# pd.set_option('display.max_columns', None)
# pd.set_option('display.expand_frame_repr', False)
# pd.set_option('max_colwidth', None)




import webvtt

# https://github.com/yt-dlp/yt-dlp/issues/1734

def fix_youtube_vtt_old(vtt_file_path) -> str:
    """Fixes Youtube's autogenerated VTT subtitles and returns a srt-formatted string"""

    

    pretty_subtitle = ''  
    previous_caption_text = ''
    previous_caption_start = '00:00:00.000'
    i = 1
    for caption in webvtt.read(vtt_file_path):

        if previous_caption_text == caption.text.strip():
            # if previous and current lines are `identical`, print the start time from the previous
            # and the end time from the current.
            pretty_subtitle += f"{previous_caption_start}  | {caption.end.strip()} |   {previous_caption_text}\n"
            # pretty_subtitle += f"{i}\n{previous_caption_start} --> {caption.end}\n{previous_caption_text}\n\n"
            i += 1

        elif previous_caption_text == caption.text.strip().split("\n")[0]: 
            # if the current caption is multiline, and the previous caption is equal to 
            # the current's first line, just ignore the first line and move on with the second.
            previous_caption_text = caption.text.strip().split("\n")[1]
            previous_caption_start = caption.start
            last_caption_end = caption.end

        else:	    
            previous_caption_text = caption.text.strip()
            previous_caption_start = caption.start.strip()

    if pretty_subtitle == '':
        for caption in webvtt.read(vtt_file_path):
            nl='\n'
            pretty_subtitle += f"{caption.start.strip()}  | {caption.end.strip()}  |  {caption.text.strip().replace(nl,'')}\n"

    return pretty_subtitle


def fix_youtube_vtt(vtt_file_path) -> str:
    """Fixes Youtube's autogenerated VTT subtitles and returns a srt-formatted string"""

    

    pretty_subtitle = ''  
    previous_caption_text = ''
    previous_caption_start = 0
    i = 1
    for caption in webvtt.read(vtt_file_path):

        if previous_caption_text == caption.text.strip():
            # if previous and current lines are `identical`, print the start time from the previous
            # and the end time from the current.
            # pretty_subtitle += f"{previous_caption_start}  | {caption.end.strip()} |   {previous_caption_text}\n"
            pretty_subtitle += f"{previous_caption_start}\t{int(1000 * caption.end_in_seconds)}\t{previous_caption_text}\n"
            # pretty_subtitle += f"{i}\n{previous_caption_start} --> {caption.end}\n{previous_caption_text}\n\n"
            i += 1

        elif previous_caption_text == caption.text.strip().split("\n")[0]: 
            # if the current caption is multiline, and the previous caption is equal to 
            # the current's first line, just ignore the first line and move on with the second.
            previous_caption_text = caption.text.strip().split("\n")[1]
            previous_caption_start = int(1000 * caption.start_in_seconds)
            last_caption_end = int(1000 * caption.end_in_seconds)

        else:	    
            previous_caption_text = caption.text.strip()
            previous_caption_start = int(1000 * caption.start_in_seconds)

    if pretty_subtitle == '':
        for caption in webvtt.read(vtt_file_path):
            nl='\n'
            pretty_subtitle += f"{int(1000 * caption.start_in_seconds)}\t{int(1000 * caption.end_in_seconds)}\t{caption.text.strip().replace(nl,'')}\n"

    return pretty_subtitle