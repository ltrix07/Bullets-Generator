from moduls import DataBase

db = DataBase('../db/data.db')

db.append_new_elements('test', [('one')])
