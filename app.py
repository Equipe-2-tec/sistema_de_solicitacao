import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash
from banco import conectar, criar_tabela

app = Flask(__name__, template_folder='front_end', static_folder='static')

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')
    
@app.route('/', methods=['GET'])
def home():
    banco_configurado = bool(os.environ.get("MYSQL_HOST"))
    return jsonify({
        "status": "online",
        "mysql_configurado": banco_configurado,
        "mensagem": "API funcionando. Envie POST para /cadastro"
    }), 200


@app.route('/cadastro', methods=['POST'])
def cadastro():
    dados = request.get_json(silent=True) or {}

    nome = dados.get('nome')
    email = dados.get('email')
    senha = dados.get('senha')

    if not nome or not email or not senha:
        return jsonify({"erro": "Preencha todos os campos"}), 400

    if len(senha) < 8:
        return jsonify({"erro": "A senha deve ter pelo menos 8 caracteres"}), 400

    conexao = None
    cursor = None

    try:
        criar_tabela()

        conexao = conectar()
        cursor = conexao.cursor()
        senha_hash = generate_password_hash(senha)

        cursor.execute("""
            INSERT INTO contas_institucionais
            (nome, email, senha, ativo, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            nome,
            email,
            senha_hash,
            False,
            'Pendente'
        ))

        conexao.commit()

        return jsonify({
            "mensagem": "Cadastro institucional realizado com sucesso!",
            "status": "Pendente",
            "informacao": "Aguarde a validação institucional para acessar o sistema."
        }), 201

    except Exception as e:
        if conexao:
            conexao.rollback()

        return jsonify({
            "erro": "Não foi possível realizar o cadastro.",
            "detalhe": str(e)
        }), 400

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


if __name__ == '__main__':
    app.run(debug=True)
