from .connection import Connection
import sqlite3
from .pool import Pool



def connect(database,iter_chunk_size=64,**kwargs):
    
    def connector():
        if isinstance(database, str):
            loc = database
        elif isinstance(database, bytes):
            loc = database.decode("utf-8")
        else:
            loc = str(database)
        return sqlite3.connect(loc,**kwargs)
 
    return Connection(connector,iter_chunk_size)