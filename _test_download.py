import _utils as u



df                            = u.pd.read_csv(r'C:\MyFiles\Code\PDB-tools_v2\in\notion_10.csv'
                                          , usecols = ['property_url','url','property_create_dt','property_done']
                                          )
df['base_link']               = df['property_url']
df['src_link']                = df['url']

df                            = df.dropna()
df['gold_link']               = df                .apply(lambda x:u.base_link_to_gold_link(x.base_link)     , axis=1 , result_type='expand')
df[['status_code','ct']]      = df                .apply(lambda x: u.first_try_url(x.gold_link)             , axis=1 , result_type='expand' )

df[['title','md']]            = df                .apply(lambda x: u.download_title_and_content(x.gold_link), axis=1 , result_type='expand' ) 
df['md_hash']                 = df                .apply(lambda x: u.generate_hash(x.md)                    , axis=1 , result_type='expand' ) 
df['gold_link_hash']          = df                .apply(lambda x: u.generate_hash(x.gold_link)             , axis=1 , result_type='expand' ) 
df['done']                    = df                .apply(lambda x: u.save_to_file(u.get_valid_filename(x.title)+'.md'
                                                                                  ,x.md
                                                                                  ,dict( aliases            = [] + [x.gold_link] + [x.base_link]
                                                                                        ,src                = x.src_link
                                                                                        ,gold_link          = x.gold_link 
                                                                                        ,gold_link_hash     = x.gold_link_hash 
                                                                                        ,test               = 'test' 
                                                                                        ,md_hash            = x.md_hash
                                                                                    #     TODO Status of downloading
                                                                                    # TODO does file was updated/downloaded manually?
                                                                                        )
                                                                                    ) 
                                                            , axis=1 )
print(df['title'])
print(df)

# u.set_meta_cont_to_file(
#   dict(url= ['https://test.gf','test'])
# , 'my content'
# , r'C:\MyFiles\Code\PDB-tools_v2\out\vault\test.md'
# )