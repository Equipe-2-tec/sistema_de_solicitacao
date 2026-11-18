import mysql.connector
import os

def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASSWORD", ""),
        database="sistema_solicitacoes"
    )