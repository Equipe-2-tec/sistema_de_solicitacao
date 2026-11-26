import os
import sys

# Garante que a raiz do projeto esteja no path para importar app.py e banco.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# A Vercel detecta a variável `app` como WSGI callable
from app import app  # noqa: F401
