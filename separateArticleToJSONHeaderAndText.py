
import requests
import trafilatura
import gensim
from pprint import pprint
import re
import os
storeFolder = os.path.dirname(__file__) + os.sep + "results" + os.sep 



url = 'https://towardsdatascience.com/building-a-python-cli-tool-to-extract-the-toc-from-markdown-files-ab5a7b9d07f2'

downloaded = trafilatura.fetch_url(url)
text=trafilatura.extract(downloaded
,include_images=True
,include_formatting=True
# , include_links=True
# ,favor_precision=True
)


def identify_headers(lines) :
    """
    Filters a list of lines to the header lines.
    Identifies headers of the 'leading-hashtag' type as well as
    headers of the 'subsequent-line' type by using regex.
    :param lines: List of header and text lines.
    :returns: List of header lines.
    """

    decompose = [{"header":"# Intro","text":[]}]
    re_hashtag_headers = r"^#+\ .*$"
    h_iter=0;
    for i, line in enumerate(lines):
        # identify headers by leading hashtags
        if re.search(re_hashtag_headers, line):
            # print("H: "+line)
            h_iter+=1
            decompose.append({"header":line,"text":[]})
        else:
            # print("T: "+line)
            decompose[h_iter]["text"].append(line)

    return decompose

f = open(storeFolder + "separateArticleToJSONHeaderAndText.json", "w", encoding="utf-8")
f.write(str(identify_headers(text.split("\n"))))
f.close()