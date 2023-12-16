import yt_dlp
import _utils as u
import os
from    pathlib import Path
from _test_tsv_agregate import tsv_to_md

url = "https://www.youtube.com/watch?v=Z8yL3zkudZU"
url = 'https://www.youtube.com/watch?v=P1u3UZQmaRo' 
url = 'https://www.youtube.com/watch?v=tNrlSai6JGA'

def download_youtube_title_and_content(  url
                                        ,folder_of_files    = 'out/'
                                        ,sub_ext            = 'vtt'
                                        ,sub_table_ext      = 'tsv'
                                        ,langs              = ["en","ru"]
                                      ):


    directory       = Path(folder_of_files)
    hash_word       = u.generate_hash(url)
    files           = list(directory.glob(hash_word+'*'))


    file_tmpl = folder_of_files + hash_word
    # langs = ["en","ru"]

    files = []
    for l in langs:
        files.append(dict(    _in  = file_tmpl + '.'+ l + '.' + sub_ext 
                            ,_out  = file_tmpl + '.'+ l + '.' + sub_table_ext 
                            ,_lang = l   ))


    ydl_opts = {
        "subtitleslangs": langs,
        'writeautomaticsub': True,
        "writesub":  True ,
        "embedsubs": True,
        'writedescription': True,
        'subtitlesformat': sub_ext,
        'skip_download': True,

        'outtmpl': file_tmpl
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(url)
        info_dict = ydl.extract_info(url, download=False)
        
        video_title = info_dict.get('title', None)
        # TODO maybe we can avoid extracting to the file by _write_subtitles(self, info_dict, filename) 
        # and write subs to variable...
        # https://stackoverflow.com/questions/63916090/extract-the-title-of-a-youtube-video-python
        su          = info_dict.get('requested_subtitles', None)
        video_lang  = info_dict.get('language', None)

    # print(video_title)
    # print(su)
        
    files =  sorted(files, key=lambda x: (x['_lang'] == video_lang),reverse=True)
    print(files)
        
    sent =''
    for f in files:
        with open(f['_out'],'w',encoding='utf8') as fl:
            fl.write('start\tend\ttext\n')
            fl.write(u.fix_youtube_vtt(f['_in']))
            sent+='# '+ f['_lang'] + '\n'
            sent += tsv_to_md(f['_out'] ,url )

            
    
    with open('out/test.md','w',encoding='utf8') as fl:
         fl.write(sent)

    return [video_title , sent]

# download_youtube_title_and_content("https://www.youtube.com/watch?v=Z8yL3zkudZU")
# download_youtube_title_and_content('https://www.youtube.com/watch?v=P1u3UZQmaRo' )
download_youtube_title_and_content('https://www.youtube.com/watch?v=tNrlSai6JGA')
