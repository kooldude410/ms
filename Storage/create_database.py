import sqlite3

conn = sqlite3.connect('characters.sqlite')

c = conn.cursor()
c.execute('''
            CREATE TABLE levelup
            (id INTEGER PRIMARY KEY ASC,
            characterId INTEGER NOT NULL, 
            userId VARCHAR(250) NOT NULL,
            xpAmount INTEGER NOT NULL,
            timestamp VARCHAR(100) NOT NULL)
        ''')

c.execute('''
            CREATE TABLE pickupitem
            (id INTEGER PRIMARY KEY ASC,
            characterId INTEGER NOT NULL, 
            itemID VARCHAR(250) NOT NULL,
            itemQuantity INTEGER NOT NULL,
            timestamp VARCHAR(100) NOT NULL)
        ''')

conn.commit()
conn.close()
