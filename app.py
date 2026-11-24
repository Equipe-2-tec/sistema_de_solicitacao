from flask import Flask, request, jsonify, render_template
from werkzeug.security import generate_password_hash
from banco import conectar, criar_tabela

app = Flask(__name__)

criar_tabela()

@app.route('/')
def home():
    return render_template('Tela_inicial.html')

@app.route('/index.html')
@app.route('/login')
def pagina_index():
    return render_template('index.html')

@app.route('/bolsa')
def pagina_bolsa():
    return render_template('Bolsa de dados.html')



@app.route('/cadastro', methods=['POST'])
def cadastro():

    dados = request.get_json(silent=True) or {}

    nome = dados.get('nome')
    email = dados.get('email')
    senha = dados.get('senha')

    if not nome or not email or not senha:
        return jsonify({
            "erro": "Preencha todos os campos"
        }), 400

    conexao = conectar()
    cursor = conexao.cursor()

    try:
        senha_hash = generate_password_hash(senha)

        cursor.execute("""
            INSERT INTO usuarios (nome, email, senha)
            VALUES (%s, %s, %s)
        """, (nome, email, senha_hash))

        conexao.commit()

        return jsonify({
            "mensagem": "Usuário cadastrado com sucesso!"
        }), 201

    except Exception:
        conexao.rollback()
        return jsonify({
            "erro": "Não foi possível realizar o cadastro"
        }), 400

    finally:
        cursor.close()
        conexao.close()


if __name__ == '__main__':
    app.run(debug=True)
