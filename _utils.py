from   pathlib import Path
import logging
import datetime
import shutil
import os
from typing import Type
import  uuid
import morss.readabilite as morss
import lxml.etree
import lxml.html
from weasyprint import HTML , CSS

def get_valid_filename(str):
    return "".join( x for x in str if (x.isalnum() or x in "._- "))

PROJECT_FOLDER  = Path(__file__).parent

TMP_FOLDER      = PROJECT_FOLDER / 'tmp'
LOG_FOLDER      = TMP_FOLDER     / 'logs'
IN_FOLDER       = PROJECT_FOLDER / 'in'
OUT_FOLDER      = PROJECT_FOLDER / 'out'

logging         .basicConfig(filename=LOG_FOLDER / get_valid_filename(str(str(datetime.datetime.now())+'.log')) ,encoding='utf8' )
logger          = logging.getLogger('PDB-tools')
logger          .setLevel(logging.DEBUG)


def Error_Handler(func):
    def Inner_Function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e :
            logger      .error(f"{func.__name__}: args:   {args}")
            logger      .error(f"{func.__name__}: kwargs: {kwargs}")
            logger      .error(e, exc_info=True)
            print(e)
            return func(*args , return_default_value = True , **kwargs)
    return Inner_Function

def get_hash(file_or_str):
    s = ''
    if isinstance(file_or_str, str):
        s = file_or_str
    elif hasattr(file_or_str, "read"): 
        s = file_or_str.read()
    return uuid.uuid5( uuid.NAMESPACE_URL , s).hex

def save_data_to_file(in_str:str, in_bytes: bytes, ext:str) -> None:
    return None

def check_program_is_installed(program: str = 'default' ) -> bool:
    return shutil.which(program) is not None

def add_program_settings(program: str) -> str:
     match program:
        case 'monolith':
            return ' -s -j  '
        case _:
            return "Something's wrong with the internet"

def get_html_from_url_as_str(url: str ) -> str:
    PROGRAMS_FOR_HTML: list[str] = ['monolith']

    best_program = next(x for x in PROGRAMS_FOR_HTML if check_program_is_installed(x))
    best_program_settings =  add_program_settings(best_program)

    # return [check_program_is_installed(x) for x in PROGRAMS_FOR_HTML ]

    return os.popen(best_program+ " " + best_program_settings + " " + url).read()


def get_readable_content(html: str) -> str:
    m_article = morss.get_article(html)
    m_bestnode = morss.get_best_node(morss.parse(html))
    if m_bestnode is not None:
        h = lxml.etree.tostring(m_bestnode, method='html')

    return m_article or m_bestnode

IMG_CSS_SETTING="""
    img {
        width       : 85%;
        height      : auto;
        }

    pre:has(code)  {
        background  : #E8E8E8;
        overflow    : auto;
        white-space : pre-wrap !important;
        }
        
/*Doesn't work VVVVV */
    th, td {
        border-bottom: 1px solid #ddd !important;
        }
    thead {
        display: table-header-group;
        background  : #E8E8E8;
    }
    table, td { border: 1px solid }
"""
DPI_SETTING= 200


def get_pdf_from_html(html: str):
    HTML(string=html).write_pdf( 'test.pdf'
                                                        , optimize_images=True 
                                                        , stylesheets=[CSS(string=IMG_CSS_SETTING)]
                                                        , dpi=DPI_SETTING)