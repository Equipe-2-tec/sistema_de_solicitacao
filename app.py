import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.security import generate_password_hash
from banco import conectar, criar_tabela

app = Flask(__name__, template_folder='front_end', static_folder='static')


# Página inicial do site (carrega o index2.html)
@app.route('/', methods=['GET'])
def home():
    return render_template('index2.html')


# Rota de verificação do status da API e do banco MySQL (acesse /status se quiser conferir)
@app.route('/status', methods=['GET'])
def status_api():
    banco_configurado = bool(os.environ.get("MYSQL_HOST"))
    return jsonify({
        "status": "online",
        "mysql_configurado": banco_configurado,
        "mensagem": "API funcionando. Envie POST para /cadastro"
    }), 200


# Carrega qualquer outra página HTML dentro de front_end (ex: /registro.html, /painel.html)
@app.route('/<pagina>.html', methods=['GET'])
def abrir_pagina(pagina):
    return render_template(f'{pagina}.html')


# Entrega o style.css, script.js e imagens que estão dentro de front_end.
# A busca ignora maiúsculas/minúsculas, então "script.js" também encontra "Script.js"
# (em servidores Linux, como Render e Railway, essa diferença faz o arquivo dar 404).
EXTENSOES_PERMITIDAS = ['css', 'js', 'png', 'jpg', 'jpeg', 'svg', 'ico']


@app.route('/<arquivo>.<ext>', methods=['GET'])
def arquivos_frontend(arquivo, ext):
    if ext.lower() not in EXTENSOES_PERMITIDAS:
        return jsonify({"erro": "Arquivo não encontrado"}), 404

    pasta = os.path.join(app.root_path, 'front_end')
    pedido = f'{arquivo}.{ext}'.lower()

    for nome in os.listdir(pasta):
        if nome.lower() == pedido:
            return send_from_directory(pasta, nome)

    return jsonify({"erro": "Arquivo não encontrado"}), 404


# Rota para salvar novos cadastros no MySQL
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
    
