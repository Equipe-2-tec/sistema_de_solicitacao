import os
import mysql.connector
from mysql.connector import Error


def conectar():
    """Conecta ao MySQL do Aiven usando variáveis de ambiente."""
    config = {
        "host": os.getenv("MYSQL_HOST", "mysql-bolsadados.h.aivencloud.com"),
        "port": int(os.getenv("MYSQL_PORT", "22478")),
        "user": os.getenv("MYSQL_USER", "avnadmin"),
        "password": os.getenv("MYSQL_PASSWORD"),
        "database": os.getenv("MYSQL_DATABASE", "defaultdb"),
        "connection_timeout": 20,
        "ssl_disabled": False,  # Aiven exige SSL
    }

    # Opcional: configure MYSQL_SSL_CA com o caminho do certificado CA do Aiven.
    ssl_ca = os.getenv("MYSQL_SSL_CA")
    if ssl_ca:
        config["ssl_ca"] = ssl_ca
        config["ssl_verify_cert"] = True
        config["ssl_verify_identity"] = True

    if not config["password"]:
        raise RuntimeError("A variável MYSQL_PASSWORD não foi configurada.")

    return mysql.connector.connect(**config)


def criar_tabela():
    conexao = None
    cursor = None

    try:
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
        )
        """

        cursor.execute(sql)
        conexao.commit()
        print("Tabela contas_institucionais criada/verificada com sucesso!")

    except Error as erro:
        print(f"Erro ao conectar/criar tabela no MySQL: {erro}")
        raise

    finally:
        if cursor is not None:
            cursor.close()
        if conexao is not None and conexao.is_connected():
            conexao.close()


if __name__ == "__main__":
    criar_tabela()
    
