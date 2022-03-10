import mysql.connector 
 
db_conn = mysql.connector.connect(host="kafka.westus.cloudapp.azure.com", user="dbuser", 
password="Password", database="events") 
 
db_cursor = db_conn.cursor() 
 
db_cursor.execute(''' 
                  DROP TABLE levelup, pickupitem 
                  ''') 
 
db_conn.commit() 
db_conn.close() 