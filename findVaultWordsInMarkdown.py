import markdown
import os
import re
import sqlite3
storeFolder = os.path.dirname(__file__) + os.sep + "results" + os.sep 


# print(storeFolder)
conn = sqlite3.connect(storeFolder+'articles.db')    
cursor = conn.cursor() 



words = cursor.execute(  '''   select id, regexp from real_vault_words 
                        ''')
words = words.fetchall()

# print(words)

mds = cursor.execute(  '''   select id, markdown from articles where markdown is not null 
                        ''')
mds = mds.fetchall()

# print(mds)

for md in mds:
    md_id,md_text=md

    for word in words:
        word_id , word_regexp = word

        # print(word_regexp)
        my_regex = r"(^|[ -])(" + word_regexp + r")([ ,:-]|$)"

        # print(my_regex)
        try:
            if re.search(my_regex, md_text, re.IGNORECASE|re.MULTILINE):
                # print(word_regexp)
                
                data = cursor.execute('''   INSERT INTO f_article_vault_words (id_article,id_vw)
                                                            VALUES ('''+ str(md_id) + ', '+ str(word_id) +'''
                                                                    )
                                                            ON CONFLICT
                                                            DO nothing
                                    ''')
        except Exception:
            print("exception!")
            print(my_regex)




conn.commit()