import yt_dlp
from _utils_old import TMP_FOLDER , IN_FOLDER, generate_hash , fix_youtube_vtt ,  logger , Error_Handler
import os
from    pathlib import Path

import subprocess
import pandas as pd

url = "https://www.youtube.com/watch?v=Z8yL3zkudZU"
url = 'https://www.youtube.com/watch?v=P1u3UZQmaRo' 
url = 'https://www.youtube.com/watch?v=tNrlSai6JGA'
url = 'https://www.youtube.com/watch?v=6oRp5UjZS28'


@Error_Handler
def tsv_to_md(file_path , url) :
    # TODO what if url whil contain &t= as parameter? 
    ret = ''


    tsv                 = pd                .read_table(Path(file_path),encoding='utf8')
    tsv                 .dropna(inplace=True)
    tsv['text_len']     = tsv['text']       .apply(lambda x :len(str(x)))
    tsv['start_sec']    = tsv['start']      .apply(lambda x :x/1000)

    groups = []
    group = 0
    cumsum = 0
    for n in tsv["text_len"]:
        if cumsum >= 1000:
            cumsum = 0
            group = group + 1
        cumsum = cumsum + n
        groups.append(group)

    # print(groups)

    new                  =  ( tsv           .groupby(groups)
                                            .agg({  'text'      :' '.join
                                                  , 'start_sec' : lambda x: x.min().round().astype(int)})
                            )
    for index, row in new.iterrows():
        ret += f' - ~~[▶]({url}&t={row["start_sec"]})~~  {row["text"]} \n'
    


    return ret

def download_youtube_audio(url,folder_of_files):
    video_path_local_list = []

    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        "paths" : dict(home = str(folder_of_files)) ,
        'outtmpl': '%(id)s.%(ext)s',
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
                                        ,sub_ext            = 'vtt'
                                        ,sub_table_ext      = 'tsv'
                                        ,langs              = ["en","ru"]
                                      ):


    directory       = TMP_FOLDER / 'download_youtube_title_and_content'
    hash_word       = generate_hash(url)
    files           = list(directory.glob(hash_word+'*'))



    file_tmpl = hash_word
    # langs = ["en","ru"]

    files = []
    for l in langs:
        files.append(dict(    _in  = file_tmpl + '.'+ l + '.' + sub_ext 
                            ,_out  = file_tmpl + '.'+ l + '.' + sub_table_ext 
                            ,_lang = l   ))


    ydl_opts = {
        # 'logger': logger,
        "subtitleslangs": langs,
        'writeautomaticsub': True,
        "writesub":  True ,
        "embedsubs": True,
        'writedescription': True,
        'subtitlesformat': sub_ext,
        'skip_download': True,
        'noplaylist': True,
        'paths' : dict(home = str(directory))  ,
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
            yt_id   = info_dict.get('id', None)
            audio_folder = IN_FOLDER / 'audio'
            if len(list(audio_folder.glob(yt_id+'*'))) == 0:
                download_youtube_audio(url,IN_FOLDER / 'audio')
            else:
                print(f'audio {yt_id} already exists')
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

    print(files)

    for f in files:
        if (directory / f['_in']).is_file():
            with (directory / f['_out']).open('w',encoding='utf8') as fl:
                fl.write('start\tend\ttext\n')
                fl.write(fix_youtube_vtt( str(directory / f['_in']) )  )
            sent+='# '+ f['_lang'] + '\n'
            sent += tsv_to_md(directory / f['_out']  ,url )

            

    # with open(folder_of_files + get_valid_filename(video_title)+'.md','w',encoding='utf8') as fl:
    #      fl.write(sent)


    # files           = directory.glob(hash_word+'*')
    # for f in files:
    #     f.unlink()



    return [video_title , sent]



# seneet= tsv_to_md('c:/MyFiles/Code/PDB-tools_v2/tmp/download_youtube_title_and_content/800510f9bc375278aacc9602757bac75.en.tsv'  ,url )

# print(type(seneet))
# print(seneet)



print(download_youtube_title_and_content(url))


# with Path(r'C:\MyFiles\Code\PDB-tools_v2\tmp\download_youtube_title_and_content\800510f9bc375278aacc9602757bac75.en.tsv').open('w',encoding='utf8') as fl:
#                     fl.write('start\tend\ttext\n')
#                     fl.write(fix_youtube_vtt( r'C:\MyFiles\Code\PDB-tools_v2\tmp\download_youtube_title_and_content\800510f9bc375278aacc9602757bac75.en.vtt' ))
