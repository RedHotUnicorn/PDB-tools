import trafilatura
import _utils as u
from html_sanitizer import Sanitizer, sanitizer as s
from bs4 import BeautifulSoup 

import readability
import requests
from markdownify import markdownify as md

import morss.readabilite as m
import lxml.etree


url="https://microsoft.github.io/lida/"
url = "https://rxresu.me/"
url = "https://stackoverflow.com/a/69178995"
url = 'https://nesslabs.com/best'  
url = "https://microsoft.github.io/generative-ai-for-beginners/#/"
url = 'https://www.reddit.com/r/Zettelkasten/s/tV7CFNg5rZ'

url = 'https://thisisdata.ru/blog/uchimsya-primenyat-okonnyye-funktsii/'
url = "https://habr.com/ru/articles/696274/"
# url = "https://habr.com/en/articles/696274/comments/"
url = "https://habr.com/ru/articles/734980/"
url = "https://t.me/zettelkasten_ch/549?embed=1&mode=tme"
url = "https://t.me/durov/272?embed=1&mode=tme"
url = "https://habr.com/en/articles/805637/"
url = 'https://thisisdata.ru/blog/kak-pravilno-organizovat-rabotu-s-gipotezami/'
# url = 'https://habr.com/en/companies/ispsystem/articles/805709/'
# url = 'https://sketchplanations.com/winking'
# url = 'https://numinous.productions/timeful/'
# url = 'https://habr.com/ru/articles/751624/'

# url = 'https://t.me/obsidian_hub/137?embed=1&mode=tme'
# url = 'https://github.com/roovo/obsidian-card-board'

DEBUG_FOLDER = u.TMP_FOLDER / '_test_readability'
DEBUG_FOLDER.mkdir(parents=True, exist_ok=True)


response = requests.get(url)
with (DEBUG_FOLDER / '01_response.html' ).open('w',encoding='utf8') as f:
    f.write(response.text)


downloaded_bs = BeautifulSoup(  response.text
                                        , features="lxml")
with (DEBUG_FOLDER / '01_downloaded_bs.html' ).open('w',encoding='utf8') as f:
    f.write(str(downloaded_bs))


html = str(downloaded_bs)

# m.tags_good.append('b')
# print(m.tags_good)

readability_morss = m.get_article(html
    # , threshold=50
    )

with (DEBUG_FOLDER / '02_sanitized_morss.html' ).open('w',encoding='utf8') as f:
    f.write(str(readability_morss))

# print(''.join(m.get_best_node(m.parse(html)).itertext()))
node = m.get_best_node(m.parse(html))
h = ''
if len(node):
    h = lxml.etree.tostring(node, method='html')
# print(h)


with (DEBUG_FOLDER / 'markdownify_morss.md' ).open('w',encoding='utf8') as f:
    f.write(md(readability_morss or h or html,autolinks = False ))