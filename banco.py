import mysql.connector


def criar_tabelas():
    conexao = mysql.connector.connect(
        host="localhost",
        user="seu_usuario",
        password="sua_senha",
        database="seu_banco",
    )
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
    criar_tabelas()
