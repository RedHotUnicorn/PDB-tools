import _utils as u



df                            = u.pd.read_csv(r'C:\MyFiles\Code\PDB-tools_v2\in\notion_10.csv'
                                          , usecols = ['property_url','url','property_create_dt','property_done']
                                          )
df['base_link']               = df['property_url']
df['src_link']                = df['url']

df                            = df.dropna()
df['gold_link']               = df                .apply(lambda x:u.base_link_to_gold_link(x.base_link)                 , axis=1 , result_type='expand' )
df['gold_hostname']           = df                .apply(lambda x:u.get_hostname(x.gold_link)                           , axis=1 , result_type='expand' )
df[['status_code','ct']]      = df                .apply(lambda x: u.first_try_url(x.gold_link)                         , axis=1 , result_type='expand' )

df[['title','md']]            = df                .apply(lambda x: u.download_article_title_and_content(x.gold_link)    , axis=1 , result_type='expand' ) 
df['md_hash']                 = df                .apply(lambda x: u.generate_hash(x.md)                                , axis=1 , result_type='expand' ) 
df['gold_link_hash']          = df                .apply(lambda x: u.generate_hash(x.gold_link)                         , axis=1 , result_type='expand' ) 
df['date']                    = df                .apply(lambda x: u.getdate()                                          , axis=1 , result_type='expand' ) 
df                            = df.dropna()
df['done']                    = df                .apply(lambda x: u.save_to_file(u.get_valid_filename(x.title+' ('+x.md_hash+')')+'.md'
                                                                                  ,x.md
                                                                                  ,dict( aliases            = [] + [x.gold_link] + [x.base_link]
                                                                                        ,date               = x.date
                                                                                        ,src                = x.src_link
                                                                                        ,gold_link          = x.gold_link 
                                                                                        ,gold_link_hash     = x.gold_link_hash 
                                                                                        ,md_hash            = x.md_hash
                                                                                        ,status_code        = x.status_code
                                                                                        ,manually_edited    = False
                                                                                        ,force_reload       = False
                                                                                        ,up                 = []
                                                                                        ,left               = [] 
                                                                                        ,right              = [] 
                                                                                        ,down               = [] 
                                                                                        ,tags               = ['#host_'+str(x.gold_hostname).strip().replace('.','_')]
                                                                                        ,settings           = []
                                                                                        )
                                                                                    ) 
                                                            , axis=1 )

print(df)
