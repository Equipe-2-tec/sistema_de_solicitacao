
from flask import Flask, request, jsonify
from banco import conectar
from datetime import datetime
import uuid

app = Flask(__name__)

@app.route('/ocorrencias', methods=['POST'])
def registrar_ocorrencia():
    dados = request.get_json(silent=True) or {}

    local = dados.get('local')
    categoria = dados.get('categoria')
    titulo = dados.get('titulo')
    descricao = dados.get('descricao')
    anexos = dados.get('anexos', [])

    if not all([local, categoria, titulo, descricao]):
        return jsonify({'erro': 'Preencha todos os campos obrigatórios'}), 400

    protocolo = str(uuid.uuid4())[:8].upper()
    data = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO ocorrencias
        (protocolo, local, categoria, titulo, descricao,
         anexos, data, situacao)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        protocolo, local, categoria, titulo, descricao,
        ', '.join(anexos), data, 'Encaminhada para gestão'
    ))

    conexao.commit()
    cursor.close()
    conexao.close()

    return jsonify({
        'mensagem': 'Ocorrência registrada com sucesso!',
        'protocolo': protocolo,
        'data': data,
        'situacao': 'Encaminhada para gestão'
    }), 201


@app.route('/ocorrencias', methods=['GET'])
def listar_ocorrencias():
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("SELECT * FROM ocorrencias ORDER BY id DESC")
    ocorrencias = cursor.fetchall()

    cursor.close()
    conexao.close()

    return jsonify(ocorrencias)


if __name__ == '__main__':
    app.run(debug=True)
