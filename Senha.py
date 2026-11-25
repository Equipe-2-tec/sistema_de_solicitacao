from recuperar_senha import (
    recuperar_senha,
    criar_tabela_recuperacao
)

app.register_blueprint(recuperar_senha)

criar_tabela_recuperacao()
