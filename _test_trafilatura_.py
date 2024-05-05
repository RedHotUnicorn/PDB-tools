import trafilatura
from bs4 import BeautifulSoup
import _utils as u
from trafilatura.xpaths import BODY_XPATH
from trafilatura.main_extractor import extract_comments, extract_content
from trafilatura.settings import DEFAULT_CONFIG, Extractor, use_config
from trafilatura.utils import load_html
from markdownify import markdownify as md
from lxml.etree import XPath
import lxml


url="https://microsoft.github.io/lida/"

# url = "https://rxresu.me/"
# url = "https://stackoverflow.com/a/69178995"
# url = 'https://nesslabs.com/best'  
# url = "https://microsoft.github.io/generative-ai-for-beginners/#/"
# url = 'https://www.reddit.com/r/Zettelkasten/s/tV7CFNg5rZ'
# url = 'https://thisisdata.ru/blog/kak-pravilno-organizovat-rabotu-s-gipotezami/'
url = 'https://thisisdata.ru/blog/uchimsya-primenyat-okonnyye-funktsii/'
# url = "https://habr.com/ru/articles/696274/"
# url = "https://habr.com/en/articles/696274/comments/"
url = "https://habr.com/ru/articles/734980/"
url = "https://t.me/zettelkasten_ch/549?embed=1&mode=tme"
url = "https://t.me/durov/272?embed=1&mode=tme"

DEBUG_FOLDER = u.TMP_FOLDER / '_test_trafilatura'

# downloaded_bs = BeautifulSoup(    trafilatura.fetch_url(url)
#                                         , features="html.parser")

# tree = lxml.html.document_fromstring(str(downloaded_bs))
# for expr in BODY_XPATH:
#     # select tree if the expression has been found
#     subtree = next((s for s in expr(tree) if s is not None), None)
#     if subtree is None:
#         continue
#     print(str(subtree.text_content() ))

html = trafilatura.fetch_url(url)
with (DEBUG_FOLDER / 'html.html' ).open('w',encoding='utf8') as f:
    f.write(html)


sent=trafilatura.extract(
    (
        html
        # .replace("<p/>", "\n<br/>\n")
        #.replace("<br/>", "\n<br/>\n")
        # .replace("</pre>", "```</pre>")
        # .replace("<pre>", "<pre>```")
        # .replace("<li>", "<li>\n")
    )
    , output_format='markdown'
    ,include_images=True
    ,include_formatting=True
     # ,favor_precision=True
    , include_links=True
     # ,favor_recall = True
    # ,include_comments=True
)

with (DEBUG_FOLDER / 'html.md' ).open('w',encoding='utf8') as f:
    f.write(str(sent))