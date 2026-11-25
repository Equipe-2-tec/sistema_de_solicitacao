
from flask import Flask, request, jsonify
from banco import conectar

app = Flask(__name__)

ambientes = [
    'Sala de aula',
    'Banheiros',
    'Biblioteca',
    'Laboratório',
    'Pátio',
    'Quadra',
    'Secretaria',
    'Refeitório',
    'Corredores',
    'Área externa',
    'Outro ambiente'
]


@app.route('/mapa', methods=['GET'])
def listar_ambientes():
    return jsonify(ambientes)


@app.route('/mapa/<local>', methods=['GET'])
def consultar_ambiente(local):
    if local not in ambientes:
        return jsonify({'erro': 'Ambiente não encontrado'}), 404

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT protocolo, categoria, titulo,
               descricao, data, situacao
        FROM ocorrencias
        WHERE local = %s
        AND situacao != 'Resolvida'
        ORDER BY id DESC
    """, (local,))

    ocorrencias = cursor.fetchall()

    cursor.close()
    conexao.close()

    return jsonify({
        'ambiente': local,
        'possui_ocorrencia': len(ocorrencias) > 0,
        'ocorrencias': ocorrencias
    })


if __name__ == '__main__':
    app.run(debug=True)
