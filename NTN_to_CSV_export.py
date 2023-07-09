import notional
import pandas as pd
import json

import PDButils as u




notion = notional.connect(auth=u.AUTH_NOTION)
db = notion.databases.retrieve(u.DB_ID_NOTION)

print(f"== {db.Title} ==")

# print the current schema
for name, prop in db.properties.items():
    print(f"{name} => {prop.type}")

query = (
    notion.databases.query(u.DB_ID_NOTION)
    .limit(2)
)

res = pd.DataFrame()

for result in query.execute():
    j = json.loads(result.json(indent=4))
    df = pd.json_normalize(j)
    res = pd.concat((res, df), axis = 0)

f = open("to_markdown.txt",'w',encoding='utf8')
f.write(res.to_markdown(index=False))
f.close()
# print(dt.to_markdown(index=False))
