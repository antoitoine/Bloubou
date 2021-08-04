from mysql.connector import connect, Error

db = None

try:
    db = connect(host="localhost", user="antoine", password="AlVick;2303", database="bloubou")
except Error as e:
    print(e)

with db.cursor(dictionary=True) as cursor:
    cursor.execute("SELECT * FROM Classement")
    for line in cursor.fetchall():
        print(line)

db.close()
