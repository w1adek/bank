"""
Run this file to create a database in MySQL.
"""

import mysql.connector

dataBase = mysql.connector.connect(
    host='localhost',
    user='root',
    password='admin',
)

cursorObject = dataBase.cursor()

cursorObject.execute('CREATE DATABASE bank')

print('Database created')