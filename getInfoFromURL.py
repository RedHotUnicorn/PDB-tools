import requests
import trafilatura
import os
from bs4 import BeautifulSoup

storeFolder = os.path.dirname(__file__) + os.sep + "results" + os.sep 

url = 'http://www.virginaustralia.com/au/en/bookings/flights/make-a-booking/'
url = 'https://arxiv.org/pdf/1709.08546.pdf'
url = 'https://static.wixstatic.com/media/b87edf_e3ba99794af542e394b7a9895bb7c8a9~mv2.png/v1/fit/w_1000%2Ch_888%2Cal_c/file.png'

url = 'https://blog.davidsha.me/how-to-automatically-update-n8n-python/'
url = 'https://habr.com/en/company/dododev/blog/722354/'

# first lets try to understand is it a some pdf or image
r = requests.head(url, allow_redirects=True)
if r.status_code == 200:
    if  "application" in r.headers['Content-Type'] or "image" in r.headers['Content-Type']:
        print("that not a text")
    else:
        downloaded = trafilatura.fetch_url(url)

        soup = BeautifulSoup(downloaded , "lxml")
        title = soup.find("meta", property="og:title")
        title = title["content"] if title else None

        og_description = soup.find("meta", property="og:description")
        og_description = og_description["content"] if og_description else None

        description = soup.find("meta", property="description")
        description = description["content"] if description else None

        print(title)
        print('\n')
        print(og_description)
        print('\n')
        print(description)
        print('\n')

        text=trafilatura.extract(downloaded
        ,include_images=True
        ,include_formatting=True
        # this links creates maybe sometimes a lot of links
        , include_links=True
        # ,favor_precision=True
        , include_comments=True
        )
        # print(text)
        f = open(storeFolder + "getInfoFromURL.md", "w", encoding='utf8')
        f.write(text)
        f.close()
