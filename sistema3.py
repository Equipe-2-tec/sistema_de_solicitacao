from flask import Flask, request, jsonify
from banco import conectar

app = Flask(__name__)

# Registrar solicitação
@app.route('/solicitacoes', methods=['POST'])
def registrar():
    dados = request.get_json(silent=True) or {}

    nome = dados.get('nome')
    titulo = dados.get('titulo')
    descricao = dados.get('descricao')

    if not nome or not titulo or not descricao:
        return jsonify({"erro": "Preencha todos os campos"}), 400

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


# Listar solicitações
@app.route('/solicitacoes', methods=['GET'])
def listar():
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM solicitacoes")
        dados = cursor.fetchall()

        return jsonify(dados)

    finally:
        cursor.close()
        conexao.close()


# Atualizar status
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
        return jsonify({"erro": "Status inválido"}), 400

    conexao = conectar()
    cursor = conexao.cursor()

    try:
        sql = """
            UPDATE solicitacoes
            SET status = %s
            WHERE id = %s
        """

        cursor.execute(sql, (status, id))
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


# Excluir solicitação
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


if __name__ == '__main__':
    app.run(debug=True)