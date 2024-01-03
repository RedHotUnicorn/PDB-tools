import _utils as u



df                            = u.pd.read_csv(r'C:\MyFiles\Code\PDB-tools_v2\in\notion_15_test.csv'
                                          , usecols = ['property_url','url','property_create_dt','property_done','property_create_dt']
                                          , parse_dates=['property_create_dt']
                                          )
df['base_link']               = df['property_url']
df['src_link']                = df['url']
df['property_create_dt']      = df['property_create_dt'].dt.tz_localize(None)
df['src_date']                = df['property_create_dt'].astype(str)

df                            = df.dropna()
df['done']                    = df                .apply(lambda x:0     if  x.property_done == False 
                                                                        or  x.property_done == "False" 
                                                                        or  x.property_done == "FALSE" 
                                                                        or  x.property_done == ""  
                                                                        else 1 
                                                                                                                        , axis=1 )
df['gold_link']               = df                .apply(lambda x:u.base_link_to_gold_link(x.base_link)                 , axis=1 , result_type='expand' )
df['gold_hostname']           = df                .apply(lambda x:u.get_hostname(x.gold_link)                           , axis=1 , result_type='expand' )

# print duplicates
dups                          = df[df.duplicated(['gold_link'])]

u.logger.info('DUPLICATES')
u.logger.info('\n'+ dups.to_markdown())

# get only undup
df                            = df                .drop_duplicates('gold_link')






df[['status_code','ct']]      = df                .apply(lambda x: u.first_try_url(x.gold_link)                         , axis=1 , result_type='expand' )

df.to_excel(r'tmp/df_after_first_try_url.xlsx')
# df                            = u.pd.read_excel(r'out/df_after_first_try_url.xlsx' )

# df[['title','md']]            = df                .apply(lambda x: u.download_article_title_and_content(x.gold_link)    , axis=1 , result_type='expand' ) 
df[['title','md']]            = df                .apply(lambda x: u.try_download(x.gold_link)            , axis=1 , result_type='expand' ) 

df['md_hash']                 = df                .apply(lambda x: u.generate_hash(x.md)                                , axis=1 , result_type='expand' ) 
df['gold_link_hash']          = df                .apply(lambda x: u.generate_hash(x.gold_link)                         , axis=1 , result_type='expand' ) 
df['date']                    = df                .apply(lambda x: u.getdate()  
                                                                                                 , axis=1 , result_type='expand' ) 

u.logger.info('BEFORE DROP NA')
u.logger.info('\n'+ df.drop(columns=['md','ct']).to_markdown())

df                            = df.dropna()
df['done']                    = df                .apply(lambda x: u.save_to_file(u.get_valid_filename(x.title.strip() +' ('+x.gold_link_hash+')')+'.md'
                                                                                  ,x.md
                                                                                  ,dict( aliases            = [] + list(set([x.gold_link, x.base_link]))
                                                                                        ,date               = x.date
                                                                                        ,src_link           = x.src_link
                                                                                        ,src_date           = x.src_date
                                                                                        ,gold_link          = x.gold_link 
                                                                                        ,gold_link_hash     = x.gold_link_hash 
                                                                                        ,md_hash            = x.md_hash
                                                                                        ,status_code        = x.status_code
                                                                                        # ,manually_edited    = False
                                                                                        # ,force_reload       = False
                                                                                        ,lock               = True
                                                                                        ,archive            = False
                                                                                        ,up                 = []
                                                                                        ,left               = [] 
                                                                                        ,right              = [] 
                                                                                        ,down               = [] 
                                                                                        ,tags               = ['#host_'+str(x.gold_hostname).strip().replace('.','_')]
                                                                                        ,settings           = []
                                                                                        )
                                                                                    ) 
                                                            , axis=1 )

u.logger.info('\n'+ df.drop(columns=['md','ct']).to_markdown())
