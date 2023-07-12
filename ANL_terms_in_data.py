import re

import PDButils as u

INPUT_TBL_1 = 'OBS_V_term'
INPUT_TBL_2 = 'articles'

OUTPUT_TBL = 'f_article_vault_words'

words = u.DB_CURSOR.execute(  f'''   select id, regexp from {INPUT_TBL_1} 
                               ''').fetchall()
# print(words)

mds = u.DB_CURSOR.execute(  ''' select id, markdown 
                                from {INPUT_TBL_2}  
                                where markdown is not null 
                        ''').fetchall()

# print(mds)

data = u.DB_CURSOR.execute(  '''   UPDATE {OUTPUT_TBL} SET isExist=0 
                            ''')
u.DB_CONNECTION.commit()


for md in mds:
    md_id,md_text=md

    for word in words:
        word_id , word_regexp = word

        # print(word_regexp)
        my_regex = r"(^|[ -/])(" + word_regexp + r")([ ,./:-]|$)"

        # print(my_regex)
        try:
            if re.search(my_regex, md_text, re.IGNORECASE|re.MULTILINE):
                # print(word_regexp)
                
                data = u.DB_CURSOR.execute('''   INSERT INTO {OUTPUT_TBL} (id_article,id_vw,isExist)
                                                            VALUES ('''+ str(md_id) + ', '+ str(word_id) +', '+'1'+'''
                                                                    )
                                                            ON CONFLICT (id_article,id_vw)
                                                            DO UPDATE 
                                                                        SET isExist = excluded.isExist
                                    ''')
        except Exception:
            print("exception!")
            print(my_regex)




u.DB_CONNECTION.commit()