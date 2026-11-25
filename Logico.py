
from flask import Flask, request, jsonify, session
from werkzeug.security import check_password_hash, generate_password_hash
from banco import conectar
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'chave-local-de-desenvolvimento')


# Criar tabela de contas institucionais
def criar_tabela():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contas_institucionais (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(150) NOT NULL UNIQUE,
            senha VARCHAR(255) NOT NULL,
            ativo BOOLEAN DEFAULT TRUE
        )
    """)

    conexao.commit()
    cursor.close()
    conexao.close()


# Criar conta de demonstração automaticamente
def criar_conta_teste():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        "SELECT id FROM contas_institucionais WHERE email = %s",
        ('teste.escola@gmail.com',)
    )

    if not cursor.fetchone():
        senha_hash = generate_password_hash('Escola12345')

        cursor.execute("""
            INSERT INTO contas_institucionais (email, senha)
            VALUES (%s, %s)
        """, ('teste.escola@gmail.com', senha_hash))

        conexao.commit()

    cursor.close()
    conexao.close()


criar_tabela()
criar_conta_teste()


# Realizar login
@app.route('/login', methods=['POST'])
def login():
    dados = request.get_json(silent=True) or request.form

    email = dados.get('email')
    senha = dados.get('senha')

    if not email or not senha:
        return jsonify({'erro': 'Preencha todos os campos'}), 400

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM contas_institucionais
        WHERE email = %s
    """, (email,))

    conta = cursor.fetchone()

    cursor.close()
    conexao.close()

    if not conta or not check_password_hash(conta['senha'], senha):
        return jsonify({'erro': 'E-mail ou senha incorretos'}), 401

    if not conta['ativo']:
        return jsonify({'erro': 'Conta institucional desativada'}), 403

    session['usuario'] = conta['email']

    return jsonify({
        'mensagem': 'Login realizado com sucesso!',
        'email': conta['email']
    })


# Encerrar sessão
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()

    return jsonify({
        'mensagem': 'Sessão encerrada com sucesso!'
    })


if __name__ == '__main__':
    app.run(debug=True)
