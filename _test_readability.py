import trafilatura
import _utils as u
import readability
import requests
from markdownify import markdownify as md

url="https://microsoft.github.io/lida/"

# url = "https://rxresu.me/"
# url = "https://stackoverflow.com/a/69178995"
# url = 'https://nesslabs.com/best'  
# url = "https://microsoft.github.io/generative-ai-for-beginners/#/"
# url = 'https://www.reddit.com/r/Zettelkasten/s/tV7CFNg5rZ'

url = 'https://thisisdata.ru/blog/uchimsya-primenyat-okonnyye-funktsii/'
# url = "https://habr.com/ru/articles/696274/"
# url = "https://habr.com/en/articles/696274/comments/"
url = "https://habr.com/ru/articles/734980/"
url = "https://t.me/zettelkasten_ch/549?embed=1&mode=tme"
url = "https://t.me/durov/272?embed=1&mode=tme"
# url = "https://habr.com/en/articles/805637/"
# url = 'https://thisisdata.ru/blog/kak-pravilno-organizovat-rabotu-s-gipotezami/'
# url = 'https://habr.com/en/companies/ispsystem/articles/805709/'
# url = 'https://sketchplanations.com/winking'
# url = 'https://numinous.productions/timeful/'

DEBUG_FOLDER = u.TMP_FOLDER / '_test_readability'
DEBUG_FOLDER.mkdir(parents=True, exist_ok=True)

html = trafilatura.fetch_url(url)
with (DEBUG_FOLDER / 'html.html' ).open('w',encoding='utf8') as f:
    f.write(html)

response = requests.get(url)
with (DEBUG_FOLDER / 'response.html' ).open('w',encoding='utf8') as f:
    f.write(str(response.content))

doc = readability.Document(html)

with (DEBUG_FOLDER / 'doc.html' ).open('w',encoding='utf8') as f:
    f.write(doc.summary())



sent=trafilatura.extract(
    (
        doc.summary()
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

with (DEBUG_FOLDER / 'trafilatura.md' ).open('w',encoding='utf8') as f:
    f.write(sent)



with (DEBUG_FOLDER / 'markdownify.md' ).open('w',encoding='utf8') as f:
    f.write(md(doc.summary(),autolinks = False))

print(doc.title())