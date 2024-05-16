import MySQLdb
import os
import dotenv
dotenv.load_dotenv()

db = MySQLdb.connect(
    host=os.getenv("shost"),
    user=os.getenv("susername"), 
    passwd=os.getenv("spassword"),
    db="'leg3ndary$btaguses'"
)

with db.cursor() as cursor:
    cursor.execute("SELECT * FROM users")
    result = cursor.fetchall()
    print(result)