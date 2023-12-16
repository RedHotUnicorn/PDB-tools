# import _utils as u
import pandas as pd





YT_VIDEO_ID     =  'Stu8h5cVzoQ' 
YT_VIDEO_ID     =  'YZhaZCLresQ'
YT_VIDEO_ID     =  'VOff0Uhr8X0'
YT_VIDEO_ID     =  'Uc75PYSYPpI'
YT_VIDEO_ID     =  'nJ660t5ku9A'
YT_VIDEO_ID     =  'tNrlSai6JGA'


YT_LINK         = f'https://www.youtube.com/watch?v={YT_VIDEO_ID}'
    
tsv = pd.read_csv(f'out/e118b05411965199a84d288c5279633a.ru.tsv', sep='\t')
# tsv = tsv.head(10)
tsv['text_len']=tsv['text'].apply(lambda x :len(x))
tsv['start_sec']=tsv['start'].apply(lambda x :x/1000)


# print(tsv)


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

new = tsv.groupby(groups).agg({'text':' '.join, 'start_sec': lambda x: x.min().round().astype(int)})

# print(new)

# print(new["text"][26])

f = open(f"out/{YT_VIDEO_ID}.md", "w",encoding='utf8')


for index, row in new.iterrows():
    str = f' - ~~[▶]({YT_LINK}&t={row["start_sec"]})~~  {row["text"]} \n'
    f.write(str)

f.close()



def tsv_to_md(file_path , url) -> str:
    ret = ''
       
    tsv                 = pd                .read_csv(file_path, sep='\t')
    tsv['text_len']     = tsv['text']       .apply(lambda x :len(x))
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

