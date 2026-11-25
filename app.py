
from flask import Flask, request, jsonify, render_template, redirect
from werkzeug.security import generate_password_hash
from banco import conectar, criar_tabela

# Configuração do Flask
app = Flask(
    __name__,
    template_folder='front_end',
    static_folder='front_end',
    static_url_path='/static'
)

app.secret_key = 'chave_secreta_sistema'

# Criar tabelas do banco de dados
criar_tabela()


# =========================
# ROTAS DAS PÁGINAS
# =========================

@app.route('/')
def home():
    return redirect('/index2.html')


@app.route('/Tela_inicial.html')
def tela_inicial():
    return render_template('Tela_inicial.html')


@app.route('/index2.html')
@app.route('/login')
def pagina_index():
    return render_template('index2.html')


@app.route('/registro.html')
@app.route('/cadastro', methods=['GET'])
def pagina_cadastro():
    return render_template('registro.html')


@app.route('/painel.html')
@app.route('/painel')
def painel():
    return render_template('painel.html')


@app.route('/mapa.html')
@app.route('/mapa')
def mapa():
    return render_template('mapa.html')


@app.route('/ocorrencias.html')
@app.route('/ocorrencias')
def ocorrencias():
    return render_template('ocorrencias.html')


@app.route('/gestao.html')
@app.route('/gestao')
def gestao():
    return render_template('gestao.html')


@app.route('/relatorios.html')
@app.route('/relatorios')
def relatorios():
    return render_template('relatorios.html')


@app.route('/comunicados.html')
@app.route('/comunicados')
def comunicados():
    return render_template('comunicados.html')


@app.route('/recuperar.html')
@app.route('/recuperar')
def recuperar():
    return render_template('recuperar.html')


@app.route('/validar-demo.html')
@app.route('/validar-demo')
def validar_demo():
    return render_template('validar-demo.html')


# =========================
# CADASTRO DE USUÁRIO
# =========================

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

    except Exception as erro:

        conexao.rollback()

        return jsonify({
            "erro": "Não foi possível realizar o cadastro"
        }), 400

    finally:

        cursor.close()
        conexao.close()


# =========================
# EXECUTAR SERVIDOR
# =========================

if __name__ == '__main__':
    app.run(debug=True)
    
