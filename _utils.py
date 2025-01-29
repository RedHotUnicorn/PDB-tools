from   pathlib import Path
import logging
import datetime
import shutil
import os
from typing import Type
import  uuid
import morss.readabilite as morss
import lxml.etree
import lxml.html
from weasyprint import HTML , CSS

def get_valid_filename(str):
    return "".join( x for x in str if (x.isalnum() or x in "._- "))

PROJECT_FOLDER  = Path(__file__).parent

TMP_FOLDER      = PROJECT_FOLDER / 'tmp'
LOG_FOLDER      = TMP_FOLDER     / 'logs'
IN_FOLDER       = PROJECT_FOLDER / 'in'
OUT_FOLDER      = PROJECT_FOLDER / 'out'

logging         .basicConfig(filename=LOG_FOLDER / get_valid_filename(str(str(datetime.datetime.now())+'.log')) ,encoding='utf8' )
logger          = logging.getLogger('PDB-tools')
logger          .setLevel(logging.DEBUG)


def Error_Handler(func):
    def Inner_Function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e :
            logger      .error(f"{func.__name__}: args:   {args}")
            logger      .error(f"{func.__name__}: kwargs: {kwargs}")
            logger      .error(e, exc_info=True)
            print(e)
            return func(*args , return_default_value = True , **kwargs)
    return Inner_Function

def get_hash(file_or_str):
    s = ''
    if isinstance(file_or_str, str):
        s = file_or_str
    elif hasattr(file_or_str, "read"): 
        s = file_or_str.read()
    return uuid.uuid5( uuid.NAMESPACE_URL , s).hex

def save_data_to_file(in_str:str, in_bytes: bytes, ext:str) -> None:
    return None

def check_program_is_installed(program: str = 'default' ) -> bool:
    return shutil.which(program) is not None

def add_program_settings(program: str) -> str:
     match program:
        case 'monolith':
            return ' -s -j  '
        case _:
            return "Something's wrong with the internet"

def get_html_from_url_as_str(url: str ) -> str:
    PROGRAMS_FOR_HTML: list[str] = ['monolith']

    best_program = next(x for x in PROGRAMS_FOR_HTML if check_program_is_installed(x))
    best_program_settings =  add_program_settings(best_program)

    # return [check_program_is_installed(x) for x in PROGRAMS_FOR_HTML ]

    return os.popen(best_program+ " " + best_program_settings + " " + url).read()


def get_readable_content(html: str) -> str:
    m_article = morss.get_article(html)
    m_bestnode = morss.get_best_node(morss.parse(html))
    if m_bestnode is not None:
        h = lxml.etree.tostring(m_bestnode, method='html')

    return m_article or m_bestnode

IMG_CSS_SETTING="""
    img {
        width       : 85%;
        height      : auto;
        }

    pre:has(code)  {
        background  : #E8E8E8;
        overflow    : auto;
        white-space : pre-wrap !important;
        }
        
/*Doesn't work VVVVV */
    th, td {
        border-bottom: 1px solid #ddd !important;
        }
    thead {
        display: table-header-group;
        background  : #E8E8E8;
    }
    table, td { border: 1px solid }
"""
DPI_SETTING= 200


def get_pdf_from_html(html: str):
    HTML(string=html).write_pdf( 'test.pdf'
                                                        , optimize_images=True 
                                                        , stylesheets=[CSS(string=IMG_CSS_SETTING)]
                                                        , dpi=DPI_SETTING)
    


##################################################
# WORK WITH SOURCE
##################################################


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
      "www.youtube.com" :['v', 'list','t','feature']
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

@Error_Handler
def get_expanded_url(url, return_default_value = False):
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
    if return_default_value : return ''
    try:
        response = requests.head(url, allow_redirects=True,verify=False, timeout=5)                                 # https://stackoverflow.com/questions/70560247/bypassing-eu-consent-request
    except:
        # for 'www.cbc.ca' and  'www.inat.fr/'. this site won't responce without uagent
        import ua_generator
        ua       = ua_generator.generate()
        response = requests.head(url, allow_redirects=True,verify=False, timeout=20,headers=ua.headers.get())   

    tmp_res = [resp.url for resp in response.history + [response] if not any(x in resp.url for x in EXCL_REDIR_ARRAY)][-1] if response.history else response.url
    return '' if not isinstance(tmp_res, str) else tmp_res



    

    """
    TODO: 
    Somehow I need to recognise such transformation... Manual variant works but every time need to fix
    - "https://sql-optimizer.streamlit.app/"
    V		
    - "https://sql-optimizer.streamlit.app/-/login?payload=MTY5ODY5OTM2NXw5YV9KTVl2SXAtTVNya2NrS3U4RlJ3UG0wQlAwQjJ3STdvcGpSZzk2Z2ZVOEc5Z1ROVHF5NWhqaGw1Q2JoZDVnUldFX1VCVTI3TlJuS0ZRZFJyNUthLXFhMVJQMzhlc2sxSThZNXZlendiN3BhR3YzODM5T0RnNXVuYjQ3eXlFN2lZeHI1TXFXRlFRS1k1VjRWejJoa2s2YnhScE9BdU1LUWpZUW9vaDBzOHhucmtvbXB4QUozY1dzeG1EU1hlMWVndkVGcm9uYjhtcnUyTjhJVWRuV0xkb0l3cWxNN1k1VVFkaTdHa2pqTG1LeHVpbUNWYm1ZMDdaZWxlTi1MZW1PellJaGp2dUZNdHBRYzh4ZEdfdHRPei1YenZ5SXE5MmExYm1XVllxZkFCZUVaSWtKV2VCOTQ3b0dwWUQ1bzl1TVR0b1N4N2F1eE5Xci1zUmE0US1XOFRDQ0NXYnNCLXNhV1NlZ1cxX0labGVpVWo0VzlfcHRJVWpIRGNGWW5UeU10Y3hhTXRRYjUyYy1CUmVrMl9kZ0VJZTViVWcwYmlFNzdrZ3kwaTdWNWdOY3JSd3FNWHFuWExKMjI3NG5qR3BpUjFCT1doSWlIdlpEMjNHVlFyd3pzR1V6UTVWbDg3TWNXcDJEYmY1a05lTDRLQ1ZUMnVVMXhmWG9VRjdoQTJFNzJpM0JyaWx4S2N6MVdZd3hoTDdwM1hnQnzhNT077_OAts4Nrn2u0_nBkbm63EQYItY5eel4wryPYg%3D%3D"
    
    """


def standartize_url(url: str) -> str:
    # <scheme>://<netloc>/<path>;<params>?<query>#<fragment>
    url       = url.replace("&amp;", "&")
    o         = urllib.parse.urlsplit(url)
    url       = o._replace(       scheme=o.scheme or "https"                 
                                , netloc=o.netloc or o.path
                                , path  ="" if o.path and not o.netloc and not o.scheme  else o.path
                                ).geturl()  
    # https://stackoverflow.com/a/61859560/5353177  
    return url

def clean_url(url: str) -> str:
    o               = urllib.parse.urlsplit(url)
    o_query         = dict(urllib.parse.parse_qsl(o.query))                         # https://gist.github.com/rokcarl/20b5bf8dd9b1998880b7
    for key in REMOVE_PARAMS_ARRAY:
        o_query.pop(key, None)     
                                                            # https://stackoverflow.com/a/70785605/5353177

    url = o._replace(query=urllib.parse.urlencode(o_query)
                            ,scheme=o.scheme or "https"
                            ).geturl()

    o_hostname          = o.hostname
    if o_hostname in STRICT_PARAMS_DICT:
        params          = STRICT_PARAMS_DICT[o_hostname]
        url             = w3lib.url.url_query_cleaner(url,params)
    if o_hostname in ADD_PARAMS_DICT:
        params_to_add   = ADD_PARAMS_DICT[o_hostname]
        url             = w3lib.url.add_or_replace_parameters(url,params_to_add)
    return url


@Error_Handler
def get_gold_url(url , return_default_value = False):
    """
    1. Standartize the curent url
    2. Parse the hostname and query
    3. If the query contains smth from REMOVE_PARAMS_ARRAY (mostly it's form RSS) -- remove it
    4. If the hostname eq to some espeitial rules -- repmve all except params from array

    """
    if return_default_value : return url

    url = standartize_url(url)
    url = get_expanded_url(url)                                   
    url = clean_url(url)   

    return url

def get_host_name(url :str) -> str:
    return urllib.parse.urlsplit(url).hostname

def get_host_url(url :str) -> str:
    o=urllib.parse.urlsplit(url)
    return o.scheme+'://'+o.netloc

