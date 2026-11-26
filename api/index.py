import os
import sys
from flask import Flask, jsonify

# Sobe um nível para achar o app.py na raiz
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Tenta importar o seu app principal
    from app import app
except Exception as e:
    # Se o app.py tiver qualquer erro, ele vai capturar aqui!
    app = Flask(__name__)
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        return jsonify({
            "ERRO_REAL_NO_PYTHON": str(e),
            "tipo_do_erro": type(e).__name__
        }), 500
