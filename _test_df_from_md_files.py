from    pathlib import Path
import  markdown
import  os
from datetime import datetime
import hashlib
import pandas as pd
import frontmatter



def get_yaml_meta_from_file(fd):
    ret     = None

    if hasattr(fd, "read"):
        f = fd.read()

    else:
        with open(fd, "r", encoding="utf-8") as f:
            f = f.read()

    md      = markdown.Markdown(extensions=['full_yaml_metadata'])
    md.convert(f)
    
    if md.Meta !="" and md.Meta!= None:
        ret = md.Meta
    
    # ret = list(filter(lambda x: x is not None, ret))

    return ret

path = r'C:\MyFiles\PKM\PDB'

# https://stackoverflow.com/questions/59197529/get-information-about-files-in-a-directory-and-print-in-a-table
directory = Path(path)
paths = []
filename = []
size = []
hashes = []
modified = []
yaml_meta = []
files = list(directory.glob('**/*.*'))
files = list(directory.glob('**/*.md'))



for file in files:
    paths.append(file.parents[0])
    filename.append(file.parts[-1])
    size.append(file.stat().st_size)
    modified.append(datetime.fromtimestamp(file.stat().st_mtime))
    with open(file, encoding="utf-8") as f:        
        hashes.append(hashlib.md5(f.read().encode()).hexdigest())
    yaml_meta.append(get_yaml_meta_from_file(os.path.join(file.parents[0],file.parts[-1]) ))



#output in to table
# report = PrettyTable()

columns    = ['Path', 'File Name'  , 'File Size'   ,'Last Modified', 'MD5 Hash', 'YAML']
data            = [paths , filename     , size          ,modified , hashes , yaml_meta]

df = pd.DataFrame(dict(zip(columns, data)))
                  
df =  df.join(pd.json_normalize(df['YAML']))


print(df)


post = frontmatter.load(r'C:\MyFiles\PKM\PDB\0 - 📥  Inbox\🎥 7 Habits that Save Me 3+ Hours a Day.md')
# print(frontmatter.dumps(post)) 

# print('-'*200)
# print(post.content)

# print('-'*200)
# print(post.metadata)



test = frontmatter.Post(content='TEEEEEEEEEEEEEST', metadata = post.metadata)
# not working bcs add metadata: 
test.metadata = post.metadata
print(frontmatter.dumps(test))
test = frontmatter.Post(content='TEEEEEEEEEEEEEST')
print('-'*200)
print(type(post))
test.metadata = dict(url= ['https://test.gf','test'] )
print(test.metadata)

print(frontmatter.dumps(test))