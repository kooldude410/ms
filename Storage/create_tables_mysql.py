import mysql.connector 
 
db_conn = mysql.connector.connect(host="kafka.westus.cloudapp.azure.com", user="dbuser", 
password="Password", database="events", port = 3306) 
 
db_cursor = db_conn.cursor() 

 
db_cursor.execute(''' 
            CREATE TABLE levelup
            (id INT NOT NULL AUTO_INCREMENT,
            characterId INTEGER NOT NULL, 
            userId VARCHAR(250) NOT NULL,
            xpAmount INTEGER NOT NULL,
            timestamp VARCHAR(100) NOT NULL,
            traceid VARCHAR(250) NOT NULL,
            CONSTRAINT levelup_pk PRIMARY KEY (id)) 
          ''') 
 
db_cursor.execute(''' 
            CREATE TABLE pickupitem
            (id INT NOT NULL AUTO_INCREMENT,
            characterId INTEGER NOT NULL, 
            itemID VARCHAR(250) NOT NULL,
            itemQuantity INTEGER NOT NULL,
            timestamp VARCHAR(100) NOT NULL,
            traceid VARCHAR(250) NOT NULL,
            CONSTRAINT pickupitem_pk PRIMARY KEY (id))
          ''') 
 
db_conn.commit() 
db_conn.close() 
