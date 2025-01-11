from   pathlib import Path
import logging
import datetime
import shutil
import os
from typing import Type

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

def get_html_from_url(url: str ) -> str:
    PROGRAMS_FOR_HTML: list[str] = ['monolith']

    best_program = next(x for x in PROGRAMS_FOR_HTML if check_program_is_installed(x))
    best_program_settings =  add_program_settings(best_program)

    # return [check_program_is_installed(x) for x in PROGRAMS_FOR_HTML ]

    return os.popen(best_program+ " " + best_program_settings + " " + url).read()
