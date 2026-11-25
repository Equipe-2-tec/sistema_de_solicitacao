
from flask import Blueprint, request, jsonify
from banco import conectar
import secrets
from datetime import datetime, timedelta

recuperar_senha = Blueprint('recuperar_senha', __name__)


# Criar tabela automaticamente
def criar_tabela_recuperacao():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recuperacao_senha (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(150) NOT NULL,
            token VARCHAR(255) NOT NULL,
            validade DATETIME NOT NULL,
            utilizado BOOLEAN DEFAULT FALSE
        )
    """)

    conexao.commit()
    cursor.close()
    conexao.close()


# Solicitar recuperação de senha
@recuperar_senha.route('/recuperar-senha', methods=['POST'])
def solicitar_recuperacao():

    dados = request.get_json(silent=True) or {}
    email = dados.get('email', '').strip().lower()

    if not email:
        return jsonify({
            "erro": "Informe o e-mail institucional."
        }), 400

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT id FROM instituicoes
            WHERE email = %s
        """, (email,))

        instituicao = cursor.fetchone()

        # Resposta genérica para não revelar se o e-mail existe
        if not instituicao:
            return jsonify({
                "mensagem": "Se o e-mail estiver cadastrado, as instruções serão enviadas."
            }), 200

        token = secrets.token_urlsafe(32)
        validade = datetime.now() + timedelta(minutes=15)

        cursor.execute("""
            INSERT INTO recuperacao_senha
            (email, token, validade)
            VALUES (%s, %s, %s)
        """, (email, token, validade))

        conexao.commit()

        # Demonstração: não envia e-mail
        return jsonify({
            "mensagem": "Solicitação recebida. Configure o envio de e-mail para concluir a recuperação."
        }), 200

    except Exception:
        conexao.rollback()
        return jsonify({
            "erro": "Não foi possível solicitar a recuperação."
        }), 500

    finally:
        cursor.close()
        conexao.close()
