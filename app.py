import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.security import generate_password_hash

try:
    from banco import conectar, criar_tabela
    _banco_erro = None
except Exception as e:
    conectar = None
    criar_tabela = None
    _banco_erro = str(e)

app = Flask(__name__, template_folder='front_end', static_folder='static')


# ===== Rotas de páginas (usadas apenas no desenvolvimento local) =====
@app.route('/', methods=['GET'])
def home():
    return render_template('index2.html')


@app.route('/<pagina>.html', methods=['GET'])
def abrir_pagina(pagina):
    return render_template(f'{pagina}.html')


@app.route('/<arquivo>.<ext>', methods=['GET'])
def arquivos_frontend(arquivo, ext):
    if ext in ['css', 'js', 'png', 'jpg', 'jpeg', 'svg', 'ico']:
        return send_from_directory('front_end', f'{arquivo}.{ext}')
    return jsonify({"erro": "Arquivo não encontrado"}), 404


# ===== Rotas da API (funcionam local e na Vercel) =====
@app.route('/api/status', methods=['GET'])
def status_api():
    banco_configurado = bool(os.environ.get("MYSQL_HOST"))
    return jsonify({
        "status": "online",
        "mysql_configurado": banco_configurado,
        "banco_importado": conectar is not None,
        "erro_banco": _banco_erro,
    }), 200


@app.route('/api/cadastro', methods=['POST'])
def cadastro():
    dados = request.get_json(silent=True) or {}

    nome  = (dados.get('nome') or '').strip()
    email = (dados.get('email') or '').strip()
    senha = dados.get('senha') or ''

    if not nome or not email or not senha:
        return jsonify({"erro": "Preencha todos os campos"}), 400

    if len(senha) < 8:
        return jsonify({"erro": "A senha deve ter pelo menos 8 caracteres"}), 400

    if conectar is None:
        return jsonify({
            "erro": "Backend de banco não configurado.",
            "detalhe": _banco_erro or "banco.py não encontrado."
        }), 503

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
        """, (nome, email, senha_hash, False, 'Pendente'))

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
    app.run(debug=True, port=5000)
