import os
import sqlite3
import subprocess
import markdown
from urlextract import URLExtract
import re

"""
DEFINE MOST USABLE VARS FOR DB CONNECTION

"""
RESULTS_FOLDER  = os.path.dirname(__file__) + os.sep + "results" + os.sep 

CSV_NOTION      = r'C:\Users\User\Downloads\notion.csv'

VAULT_PATH      = r"C:\MyFiles\PKM\PDB"
VAULT_CSV_PATH  = VAULT_PATH + os.sep + "CSV" + os.sep 

DB_FILE_NAME    = "articles.db"
DB_CONNECTION   = sqlite3.connect(RESULTS_FOLDER + DB_FILE_NAME)
DB_CURSOR       = DB_CONNECTION.cursor()


YT_DLP_EXE      = r"C:\Program Files\yt-dlp\yt-dlp.exe"
YT_DLP_FIX_VTT  = r"C:\Program Files\yt-dlp\fix_youtube_vtt.py"
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





URL_REGEXP       = r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]{2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*"
URL_PROP_REGEXP  = r"url::.*"

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

    prop_url_find       = re.findall(URL_PROP_REGEXP,text)
    prop_url            = []

    if prop_url_find:
        prop_url_search = extractor.find_urls( prop_url_find[0])
        if prop_url_search:
            prop_url    = prop_url_search[0]
    additional_urls     = extractor.find_urls( text.replace(str(prop_url),'') )


    return prop_url , additional_urls



