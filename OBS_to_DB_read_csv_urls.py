import os
import pandas as pd

import PDButils as u



df = pd.DataFrame()

for root, dirs, files in os.walk(u.VAULT_CSV_PATH):
    for file in files:
        if file.endswith(".csv"):
            # print(os.path.join(root, file))
            tmp  = pd.read_csv(os.path.join(root, file)
                                , usecols =['URL']
                                , sep=';'
                                )
            tmp['file'] = file
            
            df = df.append(tmp, ignore_index = True)
print(df)

for root, dirs, files in os.walk(u.VAULT_PATH):
    for file in files:
        if file.endswith((".md",".canvas")):
            print(u.get_URLs_from_file(root,file))

