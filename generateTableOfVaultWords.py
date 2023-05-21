import markdown
import os
import sqlite3
storeFolder = os.path.dirname(__file__) + os.sep + "results" + os.sep 


vaultPath="C:\MyFiles\PKM\PDB"
print(storeFolder)
conn = sqlite3.connect(storeFolder+'articles.db')    
cursor = conn.cursor() 



data = cursor.execute(  '''   UPDATE vault_words SET isFileExist=0 
                        ''')
conn.commit()




def getListFromMetaProp(meta, prop):
    ret = None
    if meta !="" and meta!= None:
        if prop in meta and meta[prop] != None:
            m_p = meta[prop]
            if isinstance(m_p, str):
                m_p = [m_p]
            ret = list(filter(lambda x: x is not None, m_p))
    return ret;
    

r = open(storeFolder + "generateTableOfVaultWords.txt", "w", encoding='utf8')


note_regexp = []
for root, dirs, files in os.walk(vaultPath):
    for file in files:
        if file.endswith(".md"):
            f = open(os.path.join(root, file), 'r', encoding="utf-8")
            md = markdown.Markdown(extensions=['full_yaml_metadata'])
            md.convert(f.read())

            reg_list = []
            al = getListFromMetaProp(md.Meta,'aliases')
            if al != None: reg_list.extend(al)
            rg = getListFromMetaProp(md.Meta,'regexp')
            if rg != None: reg_list.extend(rg)

            if len(reg_list) != 0:
                note_regexp.append( {"note":str(os.path.splitext(file)[0]) 
                                    # ,"regexp": "/(^|[ -])("+ '|'.join(reg_list)  +")([ ,:-]|$)/gmi" 
                                    ,"regexp": '|'.join(reg_list)  
                                    ,"isFileExist":1     })
                
                str_reg = "item.title_and_desription.search(/(^|[ -])("+ '|'.join(reg_list)  +")([ ,:-]|$)/gmi)>=0 ? item.property_tag.push('"+ str(os.path.splitext(file)[0])  +"') : console.log('so...');"
                
                
                # print(str_reg)
                # r.write(str_reg + '\n')
                
            
r.close()

print(note_regexp)

data = cursor.executemany('''   INSERT INTO vault_words (note, regexp, isFileExist)
                                            VALUES (:note
                                                    , :regexp
                                                    , :isFileExist
                                                    )
                                            ON CONFLICT(note) 
                                            DO UPDATE 
                                                SET regexp = excluded.regexp
                                                , isFileExist =  excluded.isFileExist
                    ''',note_regexp)
conn.commit()



            # if md.Meta != "" and md.Meta!= None and 'aliases' in md.Meta and md.Meta['aliases'] != None:
            #     reg_list = []
            #     if 'aliases' in md.Meta  and md.Meta['aliases'] != None:
            #         reg_list.extend(getListFromMetaProp(md.Meta['aliases']))
            #     if 'regexp' in md.Meta and md.Meta['regexp'] != None:
            #         reg_list.extend(getListFromMetaProp(md.Meta['regexp']))
            #     print("item.title_and_desription.search(/(^| )("+ '|'.join(reg_list)  +")([ ,:-\/]|$)/gmi)>=0 ? item.property_tag.push('"+ str(os.path.splitext(file)[0])  +"') : console.log('so...');")
                









                # ⚔️ Операции с деньгами.md
                # ['Долги', None]
                # 💡 Характер и его побочки.md
                # имплементация характера
                

# 'ти я решил не добавлять в волт 
# (/(^| )(map|карт.*)([ ,:]|$)/gmi) ("Map"): 
# (/(^| )(graph)([ ,:]|$)/gmi) ("Graph"): 

# (/(^| )(Youtube)([ ,:]|$)/gmi) ("Youtube"): 
# (/(^| )(github)([ ,:]|$)/gmi) ("Github"): 
# (/(^| )(Habr|Хабр)([ ,:]|$)/gmi) ("Habr"): 
# (/(^| )(Game.*)([ ,:]|$)/gmi) ("Game"): 

# (/(^| )(Color.*|Colour.*|Цвет.*)([ ,:]|$)/gmi) ("Color"): 
