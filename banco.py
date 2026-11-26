
import os
import mysql.connector
from mysql.connector import Error


def conectar():
    """Conecta ao banco MySQL hospedado no Aiven."""

    configuracao = {
        "host": os.getenv("MYSQL_HOST"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER"),
        "password": os.getenv("MYSQL_PASSWORD"),
        "database": os.getenv("MYSQL_DATABASE", "defaultdb"),
        "charset": "utf8mb4",
        "connection_timeout": 15,
        "autocommit": False,
        "ssl_disabled": False
    }

    # Certificado SSL do Aiven, caso configurado
    certificado = os.getenv("MYSQL_SSL_CA")

    if certificado:
        configuracao["ssl_ca"] = certificado
        configuracao["ssl_verify_cert"] = True

    try:
        conexao = mysql.connector.connect(**configuracao)

        if conexao.is_connected():
            return conexao

        raise ConnectionError("Não foi possível conectar ao MySQL.")

    except Error as erro:
        raise ConnectionError(
            f"Erro ao conectar ao banco de dados: {erro}"
        ) from erro


def criar_tabela():
    """Cria a tabela de contas institucionais, se não existir."""

    conexao = None
    cursor = None

    sql = """
    CREATE TABLE IF NOT EXISTS contas_institucionais (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nome VARCHAR(150) NOT NULL,
        email VARCHAR(150) NOT NULL UNIQUE,
        senha VARCHAR(255) NOT NULL,
        ativo BOOLEAN DEFAULT FALSE,
        status VARCHAR(30) DEFAULT 'Pendente',
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    try:
        conexao = conectar()
        cursor = conexao.cursor()

        cursor.execute(sql)
        conexao.commit()

        print("Tabela contas_institucionais criada/verificada com sucesso!")

    except Error as erro:
        if conexao and conexao.is_connected():
            conexao.rollback()

        print(f"Erro ao criar tabela: {erro}")
        raise

    finally:
        if cursor:
            cursor.close()

        if conexao and conexao.is_connected():
            conexao.close()


if __name__ == "__main__":
    criar_tabela()
    
