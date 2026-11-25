
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from banco import conectar

cadastro_institucional = Blueprint(
    'cadastro_institucional', __name__
)

# Criar tabela automaticamente
def criar_tabela_institucional():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS instituicoes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            escola VARCHAR(150) NOT NULL,
            email VARCHAR(150) NOT NULL UNIQUE,
            responsavel VARCHAR(150) NOT NULL,
            senha VARCHAR(255) NOT NULL,
            status VARCHAR(30) DEFAULT 'pendente'
        )
    """)

    conexao.commit()
    cursor.close()
    conexao.close()


# Cadastrar instituição
@cadastro_institucional.route(
    '/cadastro-institucional',
    methods=['POST']
)
def cadastrar():

    dados = request.get_json(silent=True) or {}

    escola = dados.get('school', '').strip()
    email = dados.get('email', '').strip().lower()
    responsavel = dados.get('owner', '').strip()
    senha = dados.get('password', '')
    confirmar = dados.get('confirm', '')

    if not all([escola, email, responsavel, senha, confirmar]):
        return jsonify({
            "erro": "Preencha todos os campos."
        }), 400

    if len(senha) < 8:
        return jsonify({
            "erro": "A senha deve ter no mínimo 8 caracteres."
        }), 400

    if senha != confirmar:
        return jsonify({
            "erro": "As senhas não coincidem."
        }), 400

    conexao = conectar()
    cursor = conexao.cursor()

    try:
        # Verificar se já existe instituição
        cursor.execute(
            "SELECT id FROM instituicoes LIMIT 1"
        )

        if cursor.fetchone():
            return jsonify({
                "erro": "Já existe um cadastro institucional."
            }), 409

        senha_hash = generate_password_hash(senha)

        cursor.execute("""
            INSERT INTO instituicoes
            (escola, email, responsavel, senha, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            escola,
            email,
            responsavel,
            senha_hash,
            'pendente'
        ))

        # Registrar histórico
        cursor.execute("""
            INSERT INTO logs (setor, acao)
            VALUES (%s, %s)
        """, (
            'Cadastro institucional',
            'Cadastro enviado para validação'
        ))

        conexao.commit()

        return jsonify({
            "mensagem": "Cadastro enviado para validação!",
            "status": "pendente"
        }), 201

    except Exception:
        conexao.rollback()
        return jsonify({
            "erro": "Erro ao realizar cadastro."
        }), 500

    finally:
        cursor.close()
        conexao.close()
