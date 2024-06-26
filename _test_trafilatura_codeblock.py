import trafilatura
from bs4 import BeautifulSoup
import _utils as u


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
# url = "https://habr.com/ru/articles/734980/"
url = "https://t.me/zettelkasten_ch/549?embed=1&mode=tme"
url = "https://t.me/durov/272?embed=1&mode=tme"

DEBUG_FOLDER = u.TMP_FOLDER / '_test_trafilatura'

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

        with (DEBUG_FOLDER / 'cleaned.html' ).open('w',encoding='utf8') as f:
            f.write(cleaned_html)

        # sent = trafilatura.bare_extraction(
        sent=trafilatura.extract(
            (
                cleaned_html
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

        print(str(sent)) 
        # for element in sent.body.iter('*'):
        #     print(element) 
        
        # .replace('```', "\n```\n")

        with (DEBUG_FOLDER / 'sent.md' ).open('w',encoding='utf8') as f:
            f.write(str(sent))
    except Exception as e:
        sent = ''
        title = ''
        print(e)

    return [ title , sent ]

download_article_title_and_content(url)



