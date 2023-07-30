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



def get_WikiLinks_from_file(path,file):

    text                = open(   os.path.join(path, file), 'r', encoding="utf-8").read()

    wiki_find       = re.findall('\[\[.*?\]\]',text)
    """
    [[Filename| alias]] --> Filename
    """
    wiki_find       = [x.replace('[','').replace(']','').split('|')[0] for x in wiki_find if  x]
    
    for root, dirs, files in os.walk(r'C:\MyFiles\PKM\PDB'):
        for file in files:
            if file.endswith(".md"):
                 # if [x for x in wiki_find if file.startswith(x)]:
                if [x for x in wiki_find if os.path.splitext(file)[0] == x ]:
                    print(file)
                    print(os.path.splitext(file)[0])

    print(wiki_find)


get_WikiLinks_from_file(r'C:\MyFiles\PKM\PDB\0 - 📥  Inbox','🧅 Импровизация.md')



