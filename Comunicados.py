
from flask import Flask, request, jsonify, session
from banco import conectar
from functools import wraps
from datetime import datetime

app = Flask(__name__)


# Verificar se o usuário é da gestão
def somente_gestao(func):
    @wraps(func)
    def verificar(*args, **kwargs):
        if 'usuario' not in session:
            return jsonify({'erro': 'Faça login primeiro'}), 401

        if session.get('perfil') != 'gestao':
            return jsonify({'erro': 'Acesso permitido somente à gestão'}), 403

        return func(*args, **kwargs)

    return verificar


# Listar comunicados publicados
@app.route('/comunicados', methods=['GET'])
def listar_comunicados():

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM comunicados
        WHERE status = 'Publicado'
        ORDER BY id DESC
    """)

    comunicados = cursor.fetchall()

    cursor.close()
    conexao.close()

    return jsonify(comunicados)


# Listar comunicados arquivados
@app.route('/comunicados/arquivados', methods=['GET'])
def listar_arquivados():

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM comunicados
        WHERE status = 'Arquivado'
        ORDER BY id DESC
    """)

    comunicados = cursor.fetchall()

    cursor.close()
    conexao.close()

    return jsonify(comunicados)


# Publicar comunicado
@app.route('/comunicados', methods=['POST'])
@somente_gestao
def publicar_comunicado():

    dados = request.get_json(silent=True) or {}

    titulo = dados.get('titulo')
    mensagem = dados.get('mensagem')

    if not titulo or not mensagem:
        return jsonify({'erro': 'Preencha todos os campos'}), 400

    data = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO comunicados
        (titulo, mensagem, data, responsavel, status)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        titulo,
        mensagem,
        data,
        session['usuario'],
        'Publicado'
    ))

    conexao.commit()
    protocolo = cursor.lastrowid

    cursor.close()
    conexao.close()

    return jsonify({
        'mensagem': 'Comunicado publicado com sucesso!',
        'id': protocolo
    }), 201


# Editar comunicado
@app.route('/comunicados/<int:id>', methods=['PUT'])
@somente_gestao
def editar_comunicado(id):

    dados = request.get_json(silent=True) or {}

    titulo = dados.get('titulo')
    mensagem = dados.get('mensagem')

    if not titulo or not mensagem:
        return jsonify({'erro': 'Informe título e mensagem'}), 400

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE comunicados
        SET titulo = %s, mensagem = %s
        WHERE id = %s AND status = 'Publicado'
    """, (titulo, mensagem, id))

    conexao.commit()
    alterados = cursor.rowcount

    cursor.close()
    conexao.close()

    if alterados == 0:
        return jsonify({'erro': 'Comunicado não encontrado'}), 404

    return jsonify({
        'mensagem': 'Comunicado atualizado com sucesso!'
    })


# Arquivar comunicado
@app.route('/comunicados/<int:id>/arquivar', methods=['PUT'])
@somente_gestao
def arquivar_comunicado(id):

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE comunicados
        SET status = 'Arquivado'
        WHERE id = %s AND status = 'Publicado'
    """, (id,))

    conexao.commit()
    alterados = cursor.rowcount

    cursor.close()
    conexao.close()

    if alterados == 0:
        return jsonify({'erro': 'Comunicado não encontrado'}), 404

    return jsonify({
        'mensagem': 'Comunicado arquivado com sucesso!'
    })


if __name__ == '__main__':
    app.run(debug=True)
