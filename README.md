# Sistema de Registro de Solicitações

## Publicar na Vercel

1. Na Vercel, abra **Add New → Project** e importe o repositório atualizado do GitHub.
2. Use a raiz do repositório como **Root Directory** e **Flask** como **Framework Preset**. Deixe **Build Command** e **Output Directory** com os valores padrão.
3. Para gravar cadastros no MySQL, adicione `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD` e `MYSQL_DATABASE` em **Environment Variables**. Se usar o certificado CA do provedor, inclua o certificado público no projeto e configure `MYSQL_SSL_CA` com o caminho relativo à raiz.
4. Clique em **Deploy**. Abra a URL gerada para acessar o login e acrescente `/api/status` para verificar se a API responde. O status informa se o host do MySQL foi configurado. A conexão é usada ao gravar um cadastro.

## Ativar confirmação de e-mail

O cadastro exige MySQL e um remetente configurado no Resend. Em **Settings → Environment Variables** na Vercel, configure estas variáveis também em **Preview** se quiser testar na branch `vercel-flask`:

- `RESEND_API_KEY` com uma chave de envio do Resend.
- `EMAIL_FROM` com um endereço autorizado em um domínio verificado no Resend.
- `EMAIL_VERIFICATION_SECRET` com uma chave aleatória de pelo menos 32 caracteres. Gere uma com `python -c "import secrets; print(secrets.token_urlsafe(32))"`.

Republique após configurar. Em `registro.html`, clique em **Enviar código por e-mail**, copie o código recebido e confirme o cadastro em até 15 minutos. O servidor grava a conta somente depois de validar o código para o mesmo endereço.

O acesso de demonstração, os dados do painel e o perfil usado pelo painel continuam vinculados ao navegador. As contas locais antigas continuam acessíveis da mesma forma.

## Rodar localmente

Com Python 3.12 e um ambiente virtual ativo:

```sh
pip install -r requirements.txt
python app.py
```

Abra http://127.0.0.1:5000.
