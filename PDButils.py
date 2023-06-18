import os
import sqlite3

# DEFINE MOST USABLE VARS
DB_FILE_NAME    = "articles.db"
DB_FILE_FOLDER  = os.path.dirname(__file__) + os.sep + "results" + os.sep 
DB_CONNECTION   = sqlite3.connect(DB_FILE_FOLDER + DB_FILE_NAME)
DB_CURSOR       = DB_CONNECTION.cursor()
