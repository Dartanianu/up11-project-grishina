import os
from database import Database

db = Database(
    host='localhost',
    port=5432,
    dbname="database",
    user="postgres",
    password="123"
)

conn = db.get_connection()

products = db.get_products()
print(products)


db.close_all()