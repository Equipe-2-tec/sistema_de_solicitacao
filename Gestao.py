
from flask import Flask, request, jsonify, session
from banco import conectar
from functools import wraps
from datetime import datetime

app = Flask(__name__)


# Verificar se o usuário está autenticado
def login_obrigatorio(func):
    @wraps(func)
    def verificar(*args, **kwargs):
        if 'usuario' not in session:
            return jsonify({'erro': 'Faça login primeiro'}), 401
        return func(*args, **kwargs)
    return verificar


# Consultar e filtrar ocorrências
@app.route('/gestao', methods=['GET'])
@login_obrigatorio
def listar_ocorrencias():

    busca = request.args.get('busca', '')
    prioridade = request.args.get('prioridade', '')
    situacao = request.args.get('situacao', '')
    categoria = request.args.get('categoria', '')

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    sql = "SELECT * FROM ocorrencias WHERE 1=1"
    valores = []

    if busca:
        sql += " AND (protocolo LIKE %s OR local LIKE %s)"
        valores.extend([f'%{busca}%', f'%{busca}%'])

    if prioridade:
        sql += " AND prioridade = %s"
        valores.append(prioridade)

    if situacao:
        sql += " AND situacao = %s"
        valores.append(situacao)

    if categoria:
        sql += " AND categoria = %s"
        valores.append(categoria)

    sql += " ORDER BY id DESC"

    cursor.execute(sql, valores)
    ocorrencias = cursor.fetchall()

    cursor.close()
    conexao.close()

    return jsonify(ocorrencias)


# Atualizar ocorrência
@app.route('/gestao/<protocolo>', methods=['PUT'])
@login_obrigatorio
def atualizar_ocorrencia(protocolo):

    dados = request.get_json(silent=True) or {}

    prioridade = dados.get('prioridade')
    situacao = dados.get('situacao')
    providencias = dados.get('providencias')
    justificativa = dados.get('justificativa')

    prioridades = ['Urgente', 'Alta', 'Média', 'Baixa']

    situacoes = [
        'Recebida',
        'Em análise',
        'Em andamento',
        'Resolvida',
        'Não resolvida'
    ]

    if prioridade and prioridade not in prioridades:
        return jsonify({'erro': 'Prioridade inválida'}), 400

    if situacao and situacao not in situacoes:
        return jsonify({'erro': 'Situação inválida'}), 400

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM ocorrencias WHERE protocolo = %s",
        (protocolo,)
    )

    ocorrencia = cursor.fetchone()

    if not ocorrencia:
        cursor.close()
        conexao.close()
        return jsonify({'erro': 'Ocorrência não encontrada'}), 404

    atualizacoes = {
        'prioridade': prioridade,
        'situacao': situacao,
        'providencias': providencias,
        'justificativa': justificativa
    }

    alteracoes = []

    for campo, novo_valor in atualizacoes.items():
        if novo_valor is not None and novo_valor != ocorrencia.get(campo):
            alteracoes.append(
                (campo, str(ocorrencia.get(campo) or ''), str(novo_valor))
            )

    if not alteracoes:
        cursor.close()
        conexao.close()
        return jsonify({'mensagem': 'Nenhuma alteração realizada'})

    for campo, valor_antigo, valor_novo in alteracoes:

        cursor.execute(
            f"UPDATE ocorrencias SET {campo} = %s WHERE protocolo = %s",
            (valor_novo, protocolo)
        )

        cursor.execute("""
            INSERT INTO historico_ocorrencias
            (protocolo, campo, valor_anterior,
             valor_novo, responsavel, data)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            protocolo,
            campo,
            valor_antigo,
            valor_novo,
            session['usuario'],
            datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        ))

    conexao.commit()
    cursor.close()
    conexao.close()

    return jsonify({
        'mensagem': 'Ocorrência atualizada com sucesso!',
        'protocolo': protocolo
    })


# Consultar histórico de alterações
@app.route('/gestao/historico/<protocolo>', methods=['GET'])
@login_obrigatorio
def consultar_historico(protocolo):

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM historico_ocorrencias
        WHERE protocolo = %s
        ORDER BY id DESC
    """, (protocolo,))

    historico = cursor.fetchall()

    cursor.close()
    conexao.close()

    return jsonify(historico)


if __name__ == '__main__':
    app.run(debug=True)
