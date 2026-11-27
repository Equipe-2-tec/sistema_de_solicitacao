import os
import re

from flask import Flask, abort, request, jsonify, render_template, send_from_directory, session
from google.auth.exceptions import GoogleAuthError
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from jinja2 import TemplateNotFound
from werkzeug.security import check_password_hash

try:
    from banco import conectar, criar_tabela
    _banco_erro = None
except Exception as e:
    conectar = None
    criar_tabela = None
    _banco_erro = str(e)

app = Flask(__name__, template_folder='front_end', static_folder='static')
app.config.update(
    SECRET_KEY=os.environ.get("APP_SESSION_SECRET") or os.urandom(32),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("VERCEL") == "1",
)


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
        "google_login_configurado": bool(os.environ.get("GOOGLE_CLIENT_ID")),
        "banco_importado": conectar is not None,
        "erro_banco": _banco_erro,
    }), 200


def dados_json():
    dados = request.get_json(silent=True)
    return dados if isinstance(dados, dict) else {}


def campo_texto(dados, nome):
    valor = dados.get(nome)
    return valor if isinstance(valor, str) else ""


def email_valido(email):
    return len(email) <= 150 and re.fullmatch(
        r"[a-z0-9_+%=-]+(?:\.[a-z0-9_+%=-]+)*@"
        r"(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,63}",
        email,
    ) is not None


def google_client_id():
    return os.environ.get("GOOGLE_CLIENT_ID", "").strip()


@app.get('/api/auth/google/config')
def google_config():
    client_id = google_client_id()
    if not client_id:
        return jsonify({"erro": "O acesso com Google ainda não foi configurado."}), 503
    return jsonify({"client_id": client_id})


@app.post('/api/auth/google')
def autenticar_google():
    client_id = google_client_id()
    if not client_id:
        return jsonify({"erro": "O acesso com Google ainda não foi configurado."}), 503

    credential = campo_texto(dados_json(), "credential").strip()
    if not credential or len(credential) > 8192:
        return jsonify({"erro": "Resposta do Google inválida."}), 400

    try:
        perfil = google_id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            client_id,
        )
    except (ValueError, GoogleAuthError):
        return jsonify({"erro": "Não foi possível confirmar esta conta Google."}), 401

    email = str(perfil.get("email") or "").strip().lower()
    google_sub = str(perfil.get("sub") or "").strip()
    email_confirmado = perfil.get("email_verified") is True

    if not email_confirmado or not email.endswith("@gmail.com") or not google_sub:
        return jsonify({"erro": "Use uma conta Gmail confirmada pelo Google."}), 403

    nome = str(perfil.get("name") or "Usuário Google").strip()[:150]
    session.clear()
    session["google_sub"] = google_sub
    session["email"] = email
    session["nome"] = nome

    return jsonify({
        "conta": {
            "id": google_sub,
            "email": email,
            "nome": nome,
        }
    })


@app.get('/api/auth/session')
def sessao_google():
    if not session.get("google_sub"):
        return jsonify({"autenticado": False}), 401
    return jsonify({
        "autenticado": True,
        "conta": {
            "id": session["google_sub"],
            "email": session.get("email", ""),
            "nome": session.get("nome", ""),
        }
    })


@app.post('/api/auth/logout')
def logout_google():
    session.clear()
    return jsonify({"mensagem": "Sessão encerrada."})


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
