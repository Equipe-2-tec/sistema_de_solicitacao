
from flask import Blueprint, jsonify
from banco import conectar

painel = Blueprint('painel', __name__)


# Consultar informações do painel
@painel.route('/api/painel', methods=['GET'])
def consultar_painel():

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    try:
        # Buscar instituição
        cursor.execute("""
            SELECT escola, status
            FROM instituicoes
            ORDER BY id DESC
            LIMIT 1
        """)

        instituicao = cursor.fetchone()

        # Contabilizar ocorrências
        cursor.execute("""
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN situacao = 'Recebida'
                    THEN 1 ELSE 0 END) AS pendentes,
                SUM(CASE WHEN situacao = 'Em andamento'
                    THEN 1 ELSE 0 END) AS andamento,
                SUM(CASE WHEN situacao = 'Resolvida'
                    THEN 1 ELSE 0 END) AS resolvidas
            FROM ocorrencias
        """)

        estatisticas = cursor.fetchone()

        # Buscar atividades recentes
        cursor.execute("""
            SELECT data, setor, acao
            FROM logs
            ORDER BY data DESC
            LIMIT 10
        """)

        atividades = cursor.fetchall()

        return jsonify({
            "instituicao": instituicao,
            "estatisticas": estatisticas,
            "atividades": atividades
        })

    finally:
        cursor.close()
        conexao.close()


# Consultar status da validação
@painel.route('/api/painel/validacao', methods=['GET'])
def consultar_validacao():

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT escola, status
            FROM instituicoes
            ORDER BY id DESC
            LIMIT 1
        """)

        instituicao = cursor.fetchone()

        if not instituicao:
            return jsonify({
                "mensagem": "Nenhuma instituição cadastrada."
            }), 404

        return jsonify(instituicao)

    finally:
        cursor.close()
        conexao.close()


# Simular aprovação institucional
@painel.route('/api/painel/aprovar', methods=['POST'])
def aprovar_demo():

    conexao = conectar()
    cursor = conexao.cursor()

    try:
        cursor.execute("""
            SELECT id FROM instituicoes
            ORDER BY id DESC
            LIMIT 1
        """)

        instituicao = cursor.fetchone()

        if not instituicao:
            return jsonify({
                "erro": "Nenhuma instituição cadastrada."
            }), 404

        id_instituicao = instituicao[0]

        cursor.execute("""
            UPDATE instituicoes
            SET status = 'aprovada'
            WHERE id = %s
        """, (id_instituicao,))

        cursor.execute("""
            INSERT INTO logs (setor, acao)
            VALUES (%s, %s)
        """, (
            "Painel principal",
            "Validação institucional simulada"
        ))

        conexao.commit()

        return jsonify({
            "mensagem": "Validação simulada com sucesso!",
            "status": "aprovada"
        }), 200

    except Exception:
        conexao.rollback()
        return jsonify({
            "erro": "Erro ao realizar validação."
        }), 500

    finally:
        cursor.close()
        conexao.close()
