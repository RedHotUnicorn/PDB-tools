import notional
import time
import PDButils as u


SRC_TABLE = 'ANL_in_NTN_url_duplicates'

    
notion = notional.connect(auth=u.AUTH_NOTION)
db = notion.databases.retrieve(u.DB_ID_NOTION)


data = u.DB_CURSOR.execute(f''' SELECT n_url 
                                FROM {SRC_TABLE}
                            ''').fetchall()




for n_url in data:
    page = notion.pages.retrieve(n_url)
    print(f"{page.Title} => {page.url}")
    time.sleep(2)
    notion.pages.update(page,Status=notional.types.Status['☠️: Duplicate'])
    # page.properties.items()
    # st = page.properties['Status']

# # print all current properties on the page...
# for name, value in page.properties.items():
#     # use the endpoint to retrieve the full property data
#     prop = notion.pages.properties.retrieve('https://www.notion.so/27393a0c652840c9becdf9f066af455a', value.id)

#     print(f"{name} [{prop.id}] => {prop}")

# update a property on the page...

# notion.pages.update(page,Status=notional.types.Status['✔️ Done'])
# notion.pages.update(page,Status=notional.types.Status['🧅'])