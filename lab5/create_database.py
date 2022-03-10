import sqlite3

conn = sqlite3.connect('characters.sqlite')

c = conn.cursor()
c.execute('''
            CREATE TABLE stats
            (id INTEGER PRIMARY KEY ASC,
            item_total INTEGER NOT NULL, 
            item_max_gain INTEGER NOT NULL,
            xp_total INTEGER NOT NULL,
            xp_max_gain INTEGER NOT NULL,
            last_updated VARCHAR(100) NOT NULL)
        ''')

conn.commit()
conn.close()
