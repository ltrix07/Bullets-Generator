from moduls import DataBase

db = DataBase('../db/data.db')

db.create_new_table_db('test', ['word'])
