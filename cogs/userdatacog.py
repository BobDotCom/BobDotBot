# import stuff
import asyncio
import sqlite3
from sqlite3 import Error
from termcolor import cprint
from discord.ext import commands

class Levels(commands.Cog, name = "User database"):
    """There are no commands in this category"""

    def __init__(self, client):
        self.client = client
        self.client.owner_id = 690420846774321221
        global onreadyblocker
        onreadyblocker = False

    @commands.Cog.listener()
    async def on_message(self, message):
        if True:
          def create_connection(path):
            connection = None
            try:
              connection = sqlite3.connect(path)
            except Error as e:
              cprint(f"The error '{e}' occurred, clearing the database file will erase all data, but will make this script useable", 'red')
            return connection
          connection = create_connection("Users.db")
          def execute_query(connection, query):
            cursor = connection.cursor()
            try:
                cursor.execute(query)
                connection.commit()
            except Error as e:
                cprint(f"The error '{e}' occurred, clearing the database file will erase all data, but will make this script useable", 'red')
          def execute_read_query(connection, query):
            cursor = connection.cursor()
            result = None
            try:
              cursor.execute(query)
              result = cursor.fetchall()
              return result
            except Error as e:
              cprint(f"The error '{e}' occurred, clearing the database file will erase all data, but will make this script useable", 'red')
          create_users_table = """
          CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userid TEXT NOT NULL,
            level INTEGER NOT NULL,
            xp INTEGER NOT NULL
          );
          """
          execute_query(connection, create_users_table)
        def get_userid(username):
            try:
              cursor = connection.cursor()
        
              sql_select_query = f"""select * from users where id = ?"""
              cursor.execute(sql_select_query, (username,))
              records = cursor.fetchall()
        
              for row in records:
                return row[1]
              cursor.close()
            except Error as error:
              print("Failed to read data from sqlite table", error)
            finally:
              if not (connection):
                  connection.close()
                  print("The SQLite connection is closed")
        def get_id(info1):
            try:
              cursor = connection.cursor()
        
              sql_select_query = f"""select id from users where userid = ?"""
              cursor.execute(sql_select_query, (info1,))
              records = cursor.fetchall()
        
              for id in records:
                return int(''.join(map(str, id)))
              cursor.close()
            except Error as error:
              print("Failed to read data from sqlite table", error)
            finally:
              if not (connection):
                  connection.close()
                  print("The SQLite connection is closed")
        def get_xp(username):
            try:
              cursor = connection.cursor()
        
              sql_select_query = f"""select * from users where id = ?"""
              cursor.execute(sql_select_query, (username,))
              records = cursor.fetchall()
        
              for row in records:
                return row[3]
              cursor.close()
            except Error as error:
              print("Failed to read data from sqlite table", error)
            finally:
              if not (connection):
                  connection.close()
                  print("The SQLite connection is closed")
        def get_level(username):
            try:
              cursor = connection.cursor()
        
              sql_select_query = f"""select * from users where id = ?"""
              cursor.execute(sql_select_query, (username,))
              records = cursor.fetchall()
        
              for row in records:
                return row[2]
              cursor.close()
            except Error as error:
              print("Failed to read data from sqlite table", error)
            finally:
              if not (connection):
                  connection.close()
                  print("The SQLite connection is closed")
        if message.author == self.client.user:
            return
        if message.author.bot: return
        author_id = str(message.author.id)
        the_id = get_id(author_id)
        userid = get_userid(the_id)
        if userid != None:
            xp = get_xp(the_id)
            newxp = xp + 1
            update_xp = f"""
            UPDATE
              users
            SET
              xp = {newxp}
            WHERE
              id = {the_id}
            """
            execute_query(connection, update_xp)
        else:
            create_users = f"""
            INSERT INTO
                users (userid, level, xp)
            VALUES
                ('{author_id}', 1, 1);
            """
            execute_query(connection, create_users)
        the_id = get_id(author_id)
        xp = get_xp(the_id)
        level = get_level(the_id)
        if xp >= round((3 * (level ** 4)) / 5):
            newlevel = level + 1
            update_level = f"""
            UPDATE
              users
            SET
              level = {newlevel}
            WHERE
              id = {the_id}
            """
            execute_query(connection, update_level)
            if not True:
                msg = await message.channel.send(f"{message.author.mention} is now level {newlevel}!")
                await asyncio.sleep(30)
                await msg.delete()

    @commands.Cog.listener()
    async def on_ready(self):
      print('UserDataCog is active')
      
              

def setup(client):
    client.add_cog(Levels(client))
