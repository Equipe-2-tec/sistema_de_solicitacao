import os
import mysql.connector


def conectar():
    return mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST"),
        port=int(os.environ.get("MYSQL_PORT", 3306)),
        user=os.environ.get("MYSQL_USER"),
        password=os.environ.get("MYSQL_PASSWORD"),
        database=os.environ.get("MYSQL_DATABASE"),
    )


def criar_tabela():
    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    CREATE TABLE IF NOT EXISTS contas_institucionais (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nome VARCHAR(150) NOT NULL,
        email VARCHAR(150) NOT NULL UNIQUE,
        senha VARCHAR(255) NOT NULL,
        ativo BOOLEAN DEFAULT FALSE,
        status VARCHAR(30) DEFAULT 'Pendente'
    );
    """

    cursor.execute(sql)
    conexao.commit()
    cursor.close()
    conexao.close()


if __name__ == "__main__":
    criar_tabela()
