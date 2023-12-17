import yt_dlp
import _utils as u
import os
from    pathlib import Path
from _test_tsv_agregate import tsv_to_md
import subprocess

url = "https://www.youtube.com/watch?v=Z8yL3zkudZU"
url = 'https://www.youtube.com/watch?v=P1u3UZQmaRo' 
url = 'https://www.youtube.com/watch?v=tNrlSai6JGA'


def download_youtube_audio(url,folder_of_files):
    video_path_local_list = []

    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'outtmpl': folder_of_files+'%(id)s.%(ext)s',
        # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
        'postprocessors': [{  # Extract audio using ffmpeg
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download(url)
        list_video_info = [ydl.extract_info(url, download=False)]

    for video_info in list_video_info:
        video_path_local_list.append(Path(f"{video_info['id']}.wav"))

    for video_path_local in video_path_local_list:
        if video_path_local.suffix == ".mp4":
            video_path_local = video_path_local.with_suffix(".wav")
            result  = subprocess.run(["ffmpeg", "-i", str(video_path_local.with_suffix(".mp4")), "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", str(video_path_local)])




def download_youtube_title_and_content(  url
                                        ,folder_of_files    = 'out/'
                                        ,sub_ext            = 'vtt'
                                        ,sub_table_ext      = 'tsv'
                                        ,langs              = ["en","ru"]
                                      ):
    # TODO create subfolder for run and creat files there
    # after run delet folder

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
        if su == None:
            download_youtube_audio(url,folder_of_files)
        video_lang  = info_dict.get('language', None)

    # print(video_title)
    # print(su)
    
    # sort by prefered lang
    files =  sorted(files, key=lambda x: (x['_lang'] == video_lang),reverse=True)
    # print(files)
        
    sent =''
    print()
    with open(list(directory.glob(hash_word+'*.description'))[0],'r',encoding='utf8') as f:
        sent +='# Description \n'
        sent += f.read()
        sent +='\n'

    for f in files:
        if Path(f['_in']).is_file():
            with open(f['_out'],'w',encoding='utf8') as fl:
                fl.write('start\tend\ttext\n')
                fl.write(u.fix_youtube_vtt(f['_in']))
                sent+='# '+ f['_lang'] + '\n'
                sent += tsv_to_md(f['_out'] ,url )

            

    with open(folder_of_files + u.get_valid_filename(video_title)+'.md','w',encoding='utf8') as fl:
         fl.write(sent)


    files           = directory.glob(hash_word+'*')
    for f in files:
        f.unlink()
    

    return [video_title , sent]

download_youtube_title_and_content("https://www.youtube.com/watch?v=Z8yL3zkudZU")
# download_youtube_title_and_content('https://www.youtube.com/watch?v=P1u3UZQmaRo' )
# download_youtube_title_and_content('https://www.youtube.com/watch?v=tNrlSai6JGA')
