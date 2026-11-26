import os

from flask import Flask, abort, request, jsonify, render_template, send_from_directory
from jinja2 import TemplateNotFound
from werkzeug.security import check_password_hash, generate_password_hash

from verificacao_email import codigo_valido, email_valido, enviar_codigo

try:
    from banco import conectar, criar_tabela
    _banco_erro = None
except Exception as e:
    conectar = None
    criar_tabela = None
    _banco_erro = str(e)

app = Flask(__name__, template_folder='front_end', static_folder='static')


# ===== Páginas e arquivos estáticos =====
@app.route('/', methods=['GET'])
def home():
    return render_template('index2.html')


@app.route('/<pagina>.html', methods=['GET'])
def abrir_pagina(pagina):
    try:
        return render_template(f'{pagina}.html')
    except TemplateNotFound:
        abort(404)


@app.route('/<arquivo>.<ext>', methods=['GET'])
def arquivos_frontend(arquivo, ext):
    if ext in ['css', 'js', 'png', 'jpg', 'jpeg', 'svg', 'ico']:
        return send_from_directory(os.path.join(app.root_path, 'public'), f'{arquivo}.{ext}')
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


def dados_json():
    dados = request.get_json(silent=True)
    return dados if isinstance(dados, dict) else {}


def campo_texto(dados, nome):
    valor = dados.get(nome)
    return valor if isinstance(valor, str) else ""


@app.post('/api/cadastro/enviar-codigo')
def cadastro_enviar_codigo():
    email = campo_texto(dados_json(), "email").strip().lower()
    if not email_valido(email):
        return jsonify({"erro": "Digite um endereço de e-mail válido."}), 400

    try:
        enviar_codigo(email)
    except (KeyError, RuntimeError, OSError):
        app.logger.warning("Falha no envio do código de confirmação.")
        return jsonify({"erro": "Não foi possível enviar o código agora."}), 503

    return jsonify({"mensagem": "Confira sua caixa de entrada e a pasta de spam."}), 202


@app.post('/api/cadastro')
def cadastro():
    dados = dados_json()
    nome = campo_texto(dados, "nome").strip()
    email = campo_texto(dados, "email").strip().lower()
    senha = campo_texto(dados, "senha")
    codigo = campo_texto(dados, "codigo").strip()

    if not nome or len(nome) > 150 or not email_valido(email) or not 8 <= len(senha) <= 128:
        return jsonify({"erro": "Confira o nome, o e-mail e a senha (8 a 128 caracteres)."}), 400

    try:
        confirmado = codigo_valido(email, codigo)
    except RuntimeError:
        return jsonify({"erro": "A confirmação por e-mail está indisponível."}), 503

    if not confirmado:
        return jsonify({"erro": "Código inválido ou expirado. Solicite um novo código."}), 400

    if conectar is None:
        return jsonify({"erro": "Banco de dados indisponível."}), 503

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
        """, (nome, email, senha_hash, False, 'Email confirmado'))

        conexao.commit()

        return jsonify({
            "mensagem": "Cadastro institucional realizado com sucesso!",
            "status": "Email confirmado"
        }), 201

    except Exception as erro:
        if conexao:
            conexao.rollback()
        if getattr(erro, "errno", None) == 1062:
            return jsonify({"erro": "Este e-mail já está cadastrado."}), 409
        app.logger.error("Falha ao gravar cadastro: %s", type(erro).__name__)
        return jsonify({"erro": "Não foi possível salvar o cadastro agora."}), 503

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


@app.post('/api/login')
def login():
    dados = dados_json()
    email = campo_texto(dados, "email").strip().lower()
    senha = campo_texto(dados, "senha")
    if not email_valido(email) or not 8 <= len(senha) <= 128:
        return jsonify({"erro": "E-mail ou senha incorretos."}), 401
    if conectar is None:
        return jsonify({"erro": "O login está indisponível."}), 503

    conexao = cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute(
            "SELECT senha FROM contas_institucionais WHERE email = %s AND status = %s",
            (email, "Email confirmado"),
        )
        conta = cursor.fetchone()
        if conta and check_password_hash(conta[0], senha):
            return jsonify({"autenticado": True})
        return jsonify({"erro": "E-mail ou senha incorretos."}), 401
    except Exception as erro:
        app.logger.error("Falha ao consultar conta: %s", type(erro).__name__)
        return jsonify({"erro": "O login está indisponível."}), 503
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


if __name__ == '__main__':
    app.run(debug=True, port=5000)
