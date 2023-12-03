import trafilatura
from bs4 import BeautifulSoup


url="https://microsoft.github.io/lida/"
# url = "https://habr.com/ru/articles/696274/"
# url = "https://habr.com/ru/articles/734980/"
# url = "https://rxresu.me/"
# url = "https://stackoverflow.com/a/69178995"  

downloaded = trafilatura.fetch_url(url)
f = open("out/_test_trafiltura_downloaded.html", "w",encoding='utf-8')
f.write(downloaded)
f.close()


downloaded_bs = BeautifulSoup(downloaded, features="html.parser")
[tag.attrs.clear() for tag in downloaded_bs.find_all(['pre','code'])]


f = open("out/_test_trafiltura_downloaded_bs.html", "w",encoding='utf-8')
f.write(downloaded_bs.prettify())
f.close()




cleaned_html = downloaded_bs.prettify()


# 
# https://github.com/adbar/trafilatura/issues/351
sent=trafilatura.extract(cleaned_html.replace("</code></pre>", "</code>```</pre>").replace("<pre><code", "<pre>```<code")
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



sent=trafilatura.extract(downloaded
	#, output_format='xml'
# ,include_images=True
 ,include_formatting=True
, include_links=True
# ,favor_precision=True
,include_comments=True
)

f = open("out/_test_trafiltura_1.6.3.md", "w",encoding='utf-8')
f.write(sent)
f.close()


