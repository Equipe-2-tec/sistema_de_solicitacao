import json
import os
import re
from urllib.request import Request, urlopen

from itsdangerous import BadData, URLSafeTimedSerializer


def email_valido(email):
    return len(email) <= 150 and re.fullmatch(
        r"[a-z0-9_+%=-]+(?:\.[a-z0-9_+%=-]+)*@"
        r"(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,63}",
        email,
    ) is not None


def serializador():
    chave = os.environ.get("EMAIL_VERIFICATION_SECRET", "")
    if len(chave) < 32:
        raise RuntimeError("Configure EMAIL_VERIFICATION_SECRET com uma chave aleatória.")
    return URLSafeTimedSerializer(chave, salt="cadastro-institucional")


def enviar_codigo(email):
    api_key = os.environ["RESEND_API_KEY"]
    remetente = os.environ["EMAIL_FROM"]
    codigo = serializador().dumps(email)
    dados = {
        "from": remetente,
        "to": [email],
        "subject": "Confirme seu e-mail para criar a conta",
        "text": (
            "Cole este código na página de cadastro do Sistema de Registro "
            f"de Solicitações. Ele vale por 15 minutos.\n\n{codigo}\n\n"
            "Se você não solicitou o cadastro, ignore esta mensagem."
        ),
    }
    requisicao = Request(
        "https://api.resend.com/emails",
        data=json.dumps(dados).encode(),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(requisicao, timeout=10):
        pass


def codigo_valido(email, codigo):
    if not codigo or len(codigo) > 512:
        return False
    try:
        return serializador().loads(codigo, max_age=900) == email
    except BadData:
        return False
