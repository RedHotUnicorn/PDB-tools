import os
import sqlite3
import subprocess

"""
DEFINE MOST USABLE VARS FOR DB CONNECTION

"""
DB_FILE_NAME    = "articles.db"
DB_FILE_FOLDER  = os.path.dirname(__file__) + os.sep + "results" + os.sep 
DB_CONNECTION   = sqlite3.connect(DB_FILE_FOLDER + DB_FILE_NAME)
DB_CURSOR       = DB_CONNECTION.cursor()


YT_DLP_EXE      = r"C:\Program Files\yt-dlp\yt-dlp.exe"
YT_DLP_FIX_VTT  = r"C:\Program Files\yt-dlp\fix_youtube_vtt.py"
# YT_DLP_GET_SUBS    = rf'''
#     "{YT_DLP_EXE}" --encoding utf-8 --no-check-certificate --sub-lang "ru,en" --write-auto-sub --write-sub --embed-subs --skip-download -o "test" "{{0}}" 1>nul 
#     && ( (      if exist test.ru.vtt (py "{YT_DLP_FIX_VTT}" test.ru.vtt && echo **###  Subs RU** && echo:  && type test.ru.*.txt && echo:  )) 
#             &   if exist test.en.vtt (py "{YT_DLP_FIX_VTT}" test.en.vtt && echo **###  Subs EN** && echo:  && type test.en.*.txt ) ) 
#     &&  del test.*
# '''.replace('\n','')

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




