import trafilatura
from bs4 import BeautifulSoup
import requests


url="https://microsoft.github.io/lida/"
# url = "https://habr.com/ru/articles/696274/"
# url = "https://habr.com/ru/articles/734980/"
# url = "https://rxresu.me/"
# url = "https://stackoverflow.com/a/69178995"
url = 'https://nesslabs.com/best'  
url = "https://microsoft.github.io/generative-ai-for-beginners/#/"
url = 'https://www.reddit.com/r/Zettelkasten/s/tV7CFNg5rZ'
url = 'https://thisisdata.ru/blog/kak-pravilno-organizovat-rabotu-s-gipotezami/'

# from requests_html import HTMLSession

# session = HTMLSession()
# headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
# r = session.get(url,headers=headers,allow_redirects=True)

# r.html.render()


# f = open("out/_test_trafiltura_requests.html", "w",encoding='utf-8')
# f.write(r.html.html)
# f.close()

downloaded = trafilatura.fetch_url(url)
f = open("out/_test_trafiltura_downloaded.html", "w",encoding='utf-8')
f.write(downloaded)
f.close()


downloaded_bs = BeautifulSoup(downloaded, features="html.parser")
[tag.attrs.clear() for tag in downloaded_bs.find_all(['pre','code',"li"])]


f = open("out/_test_trafiltura_downloaded_bs.html", "w",encoding='utf-8')
f.write(downloaded_bs.prettify(formatter=None))
f.close()




cleaned_html = downloaded_bs.prettify(formatter=None)
cleaned_html = str(downloaded_bs)


# https://github.com/adbar/trafilatura/issues/351
sent=trafilatura.extract(
    	(
            cleaned_html
            .replace("</code></pre>", "</code>```</pre>")
            .replace("<pre><code", "<pre>```<code")
            .replace("<li>", "\n<li>")
		)
	#, output_format='xml'
      # ,include_images=True
      ,include_formatting=True
      , include_links=True
      # ,favor_precision=True
      ,include_comments=True
).replace('```', "\n```\n")



f = open("out/_test_trafiltura.md", "w",encoding='utf-8')
f.write(sent)
f.close()



sent=trafilatura.extract(
    	(
            downloaded
            .replace("</code></pre>", "</code>```</pre>")
            .replace("<pre><code", "<pre>```<code")
            .replace("<li>", "<li>\n")
		)
	#, output_format='xml'
      # ,include_images=True
      ,include_formatting=True
      , include_links=True
      # ,favor_precision=True
      ,include_comments=True
).replace('```', "\n```\n")



f = open("out/_test_trafiltura_pure.md", "w",encoding='utf-8')
f.write(sent)
f.close()




