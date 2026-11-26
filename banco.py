import os
import mysql.connector
from mysql.connector import Error

# Flag em memória: evita rodar CREATE TABLE em toda requisição.
# Em serverless, cada instância "fria" roda uma vez; depois é no-op.
_tabela_criada = False


def conectar():
    """Conecta ao MySQL do Aiven usando variáveis de ambiente."""
    config = {
        "host": os.getenv("MYSQL_HOST", "mysql-bolsadados.h.aivencloud.com"),
        "port": int(os.getenv("MYSQL_PORT", "22478")),
        "user": os.getenv("MYSQL_USER", "avnadmin"),
        "password": os.getenv("MYSQL_PASSWORD"),
        "database": os.getenv("MYSQL_DATABASE", "defaultdb"),
        "connection_timeout": 20,
        "ssl_disabled": False,   # Aiven exige SSL
    }

    if not config["password"]:
        raise RuntimeError("A variável MYSQL_PASSWORD não foi configurada.")

    # CA opcional. IMPORTANTE: na Vercel o arquivo precisa estar commitado
    # no repositório (ex.: /var/task/ca.pem). Se MYSQL_SSL_CA não for
    # definido, o driver faz SSL sem verificar o certificado (funciona no Aiven).
    ssl_ca_path = os.getenv("MYSQL_SSL_CA")
    if ssl_ca_path and os.path.isfile(ssl_ca_path):
        config["ssl_ca"] = ssl_ca_path
        config["ssl_verify_cert"] = True
        config["ssl_verify_identity"] = True
    elif ssl_ca_path:
        # Env var definida mas arquivo ausente: avisa e segue sem verificação
        print(f"[banco.py] Aviso: MYSQL_SSL_CA='{ssl_ca_path}' não existe. "
              f"Seguindo com SSL sem verificação de certificado.")

    return mysql.connector.connect(**config)


def criar_tabela(forcar=False):
    global _tabela_criada
    if _tabela_criada and not forcar:
        return

    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS contas_institucionais (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(150) NOT NULL,
            email VARCHAR(150) NOT NULL UNIQUE,
            senha VARCHAR(255) NOT NULL,
            ativo BOOLEAN DEFAULT FALSE,
            status VARCHAR(30) DEFAULT 'Pendente'
        )
        """)
        conexao.commit()
        _tabela_criada = True
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
    criar_tabela(forcar=True)
