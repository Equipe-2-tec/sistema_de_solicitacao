from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"message": "Servidor Flask rodando com sucesso!"})

@app.route("/saudacao/<nome>")
def saudacao(nome):
    return jsonify({"message": f"Olá, {nome}!"})

if __name__ == "__main__":
    app.run(debug=True)
