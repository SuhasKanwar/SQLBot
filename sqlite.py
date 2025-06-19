import sqlite3

connection = sqlite3.connect('./db/sqlbot.db')

cursor = connection.cursor()

# Creating dummy database table
table_info = """
create table if not exists SQLBOT (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100),
    branch VARCHAR(100),
    email VARCHAR(100),
    cgpa FLOAT
);
"""

cursor.execute(table_info)
cursor.execute('''Insert into SQLBOT (name, branch, email, cgpa) values ('Suhas Kanwar', 'Computer Science and Engineering', 'suhas.kanwar@gmail.com', 9.27)''')
cursor.execute('''Insert into SQLBOT (name, branch, email, cgpa) values ('Suryansh Mahajan', 'Computer Science and Engineering', 'suryansh.mahajan.23cse@bmu.edu.in', 7.55)''')
cursor.execute('''Insert into SQLBOT (name, branch, email, cgpa) values ('Aditya Yadav', 'Computer Science and Engineering', 'aditya.yadav.23cse@bmu.edu.in', 8.22)''')
cursor.execute('''Insert into SQLBOT (name, branch, email, cgpa) values ('Pratyaksh Saluja', 'Computer Science and Engineering', 'pratyaksh.saluja.23cse@bmu.edu.in', 8.75)''')
cursor.execute('''Insert into SQLBOT (name, branch, email, cgpa) values ('Dron Dana', 'Computer Science and Engineering', 'dron.dana.23cse@bmu.edu.in', 7.75)''')

print("Table created and data inserted successfully.")
data = cursor.execute('''SELECT * FROM SQLBOT''').fetchall()
for row in data:
    print(row)
    
connection.commit()
connection.close()