import requests
import trafilatura
import os
from bs4 import BeautifulSoup
from urllib.parse import urlsplit
import sqlite3
import argparse


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

parser = argparse.ArgumentParser()
parser.add_argument('url')
parser.add_argument('n_url')
parser.add_argument('dt_crt')
parser.add_argument('done')
args = parser.parse_args()

url = args.url
n_url = args.n_url
dt_crt = args.dt_crt
if args.done == False or  args.done == "False" or  args.done == ""  :

    done = 0
else :
    done = 1

# print(args.done)
# print(type(args.done))

con = sqlite3.connect(storeFolder + "articles.db")
cur = con.cursor()

data = (url ,n_url,dt_crt,done)
# print(data)
try:
    cur.execute("INSERT INTO url (url,n_url,dt_crt,done) VALUES(?,?,?,?)", data)
    con.commit()  
except sqlite3.Error as er:
    print("duplicate")
    print(n_url)
con.close()

