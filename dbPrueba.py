

#!/usr/bin/python
# datademo.py 
# a simple script to pull some data from MySQL

import MySQLdb

try:
        db = MySQLdb.connect(host="192.168.1.4", user="student", passwd="student", db="demo")

#create a cursor for the select
        cur = db.cursor()

#execute an sql query
        cur.execute("SELECT first_name,last_name FROM demo.employees")

##Iterate

        for row in cur.fetchall() :
              #data from rows
                firstname = str(row[0])
                lastname = str(row[1])

      #print 
                print ("This Person's name is " + firstname + " " + lastname)
        
        a=str(cur.rownumber)
        print(a)
        
except Exception as e:
    print (e)
    print ("No hay conexion")
    
finally:
# close the cursor
        cur.close()

# close the connection
        db.close ()
