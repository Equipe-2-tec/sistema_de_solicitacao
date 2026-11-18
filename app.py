
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from banco import conectar

app = Flask(__name__)
CORS(app)


# =====================================
# CADASTRAR USUARIO
# =====================================

@app.route('/cadastro', methods=['POST'])
def cadastrar():

    dados = request.get_json(silent=True) or {}

    nome = dados.get('nome')
    email = dados.get('email')
    login = dados.get('login')
    senha = dados.get('senha')

    if not all([nome, email, login, senha]):
        return jsonify({"erro": "Preencha todos os campos"}), 400

    conexao = conectar()
    cursor = conexao.cursor()

    try:
        senha_hash = generate_password_hash(senha)

        sql = """
            INSERT INTO usuarios
            (nome, email, login, senha)
            VALUES (%s, %s, %s, %s)
        """

        cursor.execute(sql, (nome, email, login, senha_hash))
        conexao.commit()

        return jsonify({
            "mensagem": "Cadastro realizado com sucesso!"
        }), 201

    except mysql.connector.IntegrityError:
        return jsonify({
            "erro": "E-mail ou usuário já cadastrado."
        }), 409

    finally:
        cursor.close()
        conexao.close()


# =====================================
# REALIZAR LOGIN
# =====================================

@app.route('/login', methods=['POST'])
def login_usuario():

    dados = request.get_json(silent=True) or {}

    usuario = dados.get('login')
    senha = dados.get('senha')

    if not usuario or not senha:
        return jsonify({
            "erro": "Informe login e senha."
        }), 400

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM usuarios WHERE login = %s",
            (usuario,)
        )

        resultado = cursor.fetchone()

        if resultado and check_password_hash(
            resultado['senha'], senha
        ):
            return jsonify({
                "mensagem": "Login realizado com sucesso!",
                "nome": resultado['nome'],
                "id": resultado['id']
            })

        return jsonify({
            "erro": "Login ou senha incorretos."
        }), 401

    finally:
        cursor.close()
        conexao.close()


# =====================================
# REGISTRAR SOLICITACAO
# =====================================

@app.route('/solicitacoes', methods=['POST'])
def registrar():

    dados = request.get_json(silent=True) or {}

    nome = dados.get('nome')
    titulo = dados.get('titulo')
    descricao = dados.get('descricao')

    if not nome or not titulo or not descricao:
        return jsonify({
            "erro": "Preencha todos os campos"
        }), 400

    conexao = conectar()
    cursor = conexao.cursor()

    try:
        sql = """
            INSERT INTO solicitacoes
            (nome, titulo, descricao)
            VALUES (%s, %s, %s)
        """

        cursor.execute(sql, (nome, titulo, descricao))
        conexao.commit()

        return jsonify({
            "mensagem": "Solicitação registrada!",
            "id": cursor.lastrowid
        }), 201

    finally:
        cursor.close()
        conexao.close()


# =====================================
# LISTAR SOLICITACOES
# =====================================

@app.route('/solicitacoes', methods=['GET'])
def listar():

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM solicitacoes ORDER BY id DESC"
        )

        dados = cursor.fetchall()

        return jsonify(dados)

    finally:
        cursor.close()
        conexao.close()


# =====================================
# ATUALIZAR STATUS
# =====================================

@app.route('/solicitacoes/<int:id>', methods=['PUT'])
def atualizar(id):

    dados = request.get_json(silent=True) or {}
    status = dados.get('status')

    status_validos = [
        'Pendente',
        'Em andamento',
        'Concluída'
    ]

    if status not in status_validos:
        return jsonify({
            "erro": "Status inválido"
        }), 400

    conexao = conectar()
    cursor = conexao.cursor()

    try:
        cursor.execute(
            """
            UPDATE solicitacoes
            SET status = %s
            WHERE id = %s
            """,
            (status, id)
        )

        conexao.commit()

        if cursor.rowcount == 0:
            return jsonify({
                "erro": "Solicitação não encontrada"
            }), 404

        return jsonify({
            "mensagem": "Status atualizado!"
        })

    finally:
        cursor.close()
        conexao.close()


# =====================================
# EXCLUIR SOLICITACAO
# =====================================

@app.route('/solicitacoes/<int:id>', methods=['DELETE'])
def excluir(id):

    conexao = conectar()
    cursor = conexao.cursor()

    try:
        cursor.execute(
            "DELETE FROM solicitacoes WHERE id = %s",
            (id,)
        )

        conexao.commit()

        if cursor.rowcount == 0:
            return jsonify({
                "erro": "Solicitação não encontrada"
            }), 404

        return jsonify({
            "mensagem": "Solicitação excluída!"
        })

    finally:
        cursor.close()
        conexao.close()


# =====================================
# INICIAR SERVIDOR
# =====================================

if __name__ == '__main__':
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True
    )
