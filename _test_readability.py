import trafilatura
import _utils as u
from html_sanitizer import Sanitizer, sanitizer as s
from bs4 import BeautifulSoup 

import readability
import requests
from markdownify import markdownify as md

import morss.readabilite as m


url="https://microsoft.github.io/lida/"

# url = "https://rxresu.me/"
# url = "https://stackoverflow.com/a/69178995"
# url = 'https://nesslabs.com/best'  
# url = "https://microsoft.github.io/generative-ai-for-beginners/#/"
# url = 'https://www.reddit.com/r/Zettelkasten/s/tV7CFNg5rZ'

url = 'https://thisisdata.ru/blog/uchimsya-primenyat-okonnyye-funktsii/'
# url = "https://habr.com/ru/articles/696274/"
# url = "https://habr.com/en/articles/696274/comments/"
# url = "https://habr.com/ru/articles/734980/"
url = "https://t.me/zettelkasten_ch/549?embed=1&mode=tme"
# url = "https://t.me/durov/272?embed=1&mode=tme"
# url = "https://habr.com/en/articles/805637/"
# url = 'https://thisisdata.ru/blog/kak-pravilno-organizovat-rabotu-s-gipotezami/'
# url = 'https://habr.com/en/companies/ispsystem/articles/805709/'
# url = 'https://sketchplanations.com/winking'
# url = 'https://numinous.productions/timeful/'
# url = 'https://habr.com/ru/articles/751624/'

# url = 'https://t.me/obsidian_hub/137?embed=1&mode=tme'
url = 'https://github.com/roovo/obsidian-card-board'

DEBUG_FOLDER = u.TMP_FOLDER / '_test_readability'
DEBUG_FOLDER.mkdir(parents=True, exist_ok=True)

# html = trafilatura.fetch_url(url)
# with (DEBUG_FOLDER / '01_html.html' ).open('w',encoding='utf8') as f:
#     f.write(html)

response = requests.get(url)
with (DEBUG_FOLDER / '01_response.html' ).open('w',encoding='utf8') as f:
    f.write(response.text)


downloaded_bs = BeautifulSoup(  response.text
                                        , features="lxml")
with (DEBUG_FOLDER / '01_downloaded_bs.html' ).open('w',encoding='utf8') as f:
    f.write(str(downloaded_bs))
    # f.write(str(downloaded_bs.prettify()))

# html = str(downloaded_bs.prettify())
html = str(downloaded_bs)

body = "".join(str(item) for item in downloaded_bs.body.contents)
head = "".join(str(item) for item in downloaded_bs.head.contents)






########################################################################



# ADDITIONAL_SETTINGS = {
#     "tags": {
#         "a", "h1", "h2", "h3", "strong", "em", "p", "ul", "ol",
#         "li", "br", "sub", "sup", "hr", "div" , "html","title" , "body" , "head"
#     },
#     "empty": {"hr", "a", "br", "div" , "html","title" , "body" , "head"},
# }

# sanitizer = Sanitizer(ADDITIONAL_SETTINGS)  # default configuration




# # Make a copy
# html_settings = dict(s.DEFAULT_SETTINGS)

# # Add your changes
# html_settings['tags'].add('html')
# html_settings['empty'].add('html')
# html_settings['attributes'].update({'html': () })
# html_settings['tags'].add('head')
# html_settings['empty'].add('head')
# html_settings['attributes'].update({'head': () })
# html_settings['tags'].add('body')
# html_settings['empty'].add('body')
# html_settings['attributes'].update({'body': () })
# html_settings['tags'].add('title')
# html_settings['empty'].add('title')
# html_settings['attributes'].update({'title': () })
# html_settings['tags'].add('div')
# html_settings['empty'].add('div')
# html_settings['attributes'].update({'div': () })
# html_settings['tags'].add('code')
# # html_settings['empty'].add('code')
# # html_settings['attributes'].update({'code': ('class') })





# sanitizer = Sanitizer(settings=html_settings)
# sanitized = sanitizer.sanitize(html)
# with (DEBUG_FOLDER / '02_sanitized.html' ).open('w',encoding='utf8') as f:
#     f.write(sanitized)

# sanitized_body = sanitizer.sanitize(body)
# with (DEBUG_FOLDER / '02_sanitized_body.html' ).open('w',encoding='utf8') as f:
#     f.write(sanitized_body)

# sanitized_head = sanitizer.sanitize(head)
# with (DEBUG_FOLDER / '02_sanitized_head.html' ).open('w',encoding='utf8') as f:
#     f.write(sanitized_head)


# doc = readability.Document(sanitized_body)
# with (DEBUG_FOLDER / '03_readability.html' ).open('w',encoding='utf8') as f:
#     f.write(doc.summary())


readability_morss = m.get_article(html,debug=True)

with (DEBUG_FOLDER / '02_sanitized_morss.html' ).open('w',encoding='utf8') as f:
    f.write(readability_morss)


# ######################################################
# with (DEBUG_FOLDER / 'markdownify_sanitized_body.md' ).open('w',encoding='utf8') as f:
#     f.write(md(doc.summary(),autolinks = False))


# with (DEBUG_FOLDER / 'markdownify_html.md' ).open('w',encoding='utf8') as f:
#     f.write(md(html,autolinks = False))

# with (DEBUG_FOLDER / 'markdownify_body.md' ).open('w',encoding='utf8') as f:
#     f.write(md(body,autolinks = False))

with (DEBUG_FOLDER / 'markdownify_morss.md' ).open('w',encoding='utf8') as f:
    f.write(md(readability_morss,autolinks = False))

