import os
import PDButils as u


OUTPUT_TBL  = 'OBS_term'


data = u.DB_CURSOR.execute( f'''   UPDATE {OUTPUT_TBL}  SET isFileExist=0 
                            ''')
u.DB_CONNECTION.commit()



note_regexp = []

for root, dirs, files in os.walk(u.VAULT_PATH):
    for file in files:
        if file.endswith(".md"):

            reg_list = []
            al = u.get_Meta_Property_from_MD(root, file ,'aliases')
            if al != None: reg_list.extend(al)
            rg = u.get_Meta_Property_from_MD(root, file ,'regexp')
            if rg != None: reg_list.extend(rg)

            if len(reg_list) != 0:
                note_regexp.append( {"note":str(os.path.splitext(file)[0]) 
                                    # ,"regexp": "/(^|[ -])("+ '|'.join(reg_list)  +")([ ,:-]|$)/gmi" 
                                    ,"regexp": '|'.join(reg_list)  
                                    ,"isFileExist":1     })
                

data = u.DB_CURSOR.executemany(f'''   INSERT INTO {OUTPUT_TBL} (note, regexp, isFileExist)
                                            VALUES (:note
                                                    , :regexp
                                                    , :isFileExist
                                                    )
                                            ON CONFLICT(note) 
                                            DO UPDATE 
                                                SET regexp = excluded.regexp
                                                , isFileExist =  excluded.isFileExist
                    ''',note_regexp)
u.DB_CONNECTION.commit()
