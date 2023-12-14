import yt_dlp
import _utils as u

url = "https://www.youtube.com/watch?v=Z8yL3zkudZU"
url = 'https://www.youtube.com/watch?v=P1u3UZQmaRo' 

file1 = 'out/' + u.generate_hash(url) +'.vtt'
file2 = 'out/' + u.generate_hash(url) +'.vtt'

ydl_opts = {
      'writeautomaticsub': True,
      'writedescription': True,
        'subtitlesformat': 'vtt',
    'skip_download': True,
    "sub_lang": "ru,en" ,
    "write_sub":  True ,
    "embed_subs": True,
    'outtmpl': file1
}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])
    print('')

f = open('out/d5cce4b58b67502890cb3286833020da.vtt.en.fixed.vtt','w')
f.write(u.fix_youtube_vtt('out/d5cce4b58b67502890cb3286833020da.vtt.en.vtt'))
f.close() 


