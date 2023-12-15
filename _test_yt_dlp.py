import yt_dlp
import _utils as u
import os

url = "https://www.youtube.com/watch?v=Z8yL3zkudZU"
url = 'https://www.youtube.com/watch?v=P1u3UZQmaRo' 
url = 'https://www.youtube.com/watch?v=tNrlSai6JGA' 

file_tmpl = 'out/' + u.generate_hash(url)
langs = ["en","ru"]

files = []
for l in langs:
    files.append(dict( _in = file_tmpl + '.'+ l + '.vtt' 
                      ,_out = file_tmpl + '.'+ l + '.tsv'  ))


ydl_opts = {
    "subtitleslangs": langs,
    'writeautomaticsub': True,
    "writesub":  True ,
    "embedsubs": True,
    'writedescription': True,
    'subtitlesformat': 'vtt',
    'skip_download': True,

    'verbose': True,
    
    
    
    'outtmpl': file_tmpl
}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])

# f = open('out/d5cce4b58b67502890cb3286833020da.vtt.en.fixed.vtt','w')
# f.write(u.fix_youtube_vtt('out/d5cce4b58b67502890cb3286833020da.vtt.en.vtt'))
# f.close() 

for f in files:
    with open(f['_out'],'w',encoding='utf8') as fl:
        fl.write(u.fix_youtube_vtt(f['_in']))
    if os.path.exists(f['_in']): os.remove(f['_in'])

