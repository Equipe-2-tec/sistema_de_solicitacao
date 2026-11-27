# Sistema de Registro de Solicitações

## Publicar na Vercel

1. Na Vercel, abra **Add New → Project** e importe o repositório atualizado do GitHub.
2. Use a raiz do repositório como **Root Directory** e **Flask** como **Framework Preset**. Deixe **Build Command** e **Output Directory** com os valores padrão.
3. Para manter o acesso antigo por senha no MySQL, adicione `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD` e `MYSQL_DATABASE` em **Environment Variables**. Se usar o certificado CA do provedor, inclua o certificado público no projeto e configure `MYSQL_SSL_CA` com o caminho relativo à raiz.
4. Clique em **Deploy**. Abra a URL gerada para acessar o login e acrescente `/api/status` para verificar se a API responde.

## Ativar o acesso com Google

1. No Google Cloud, configure a tela de consentimento OAuth e crie uma credencial do tipo **OAuth client ID → Web application**.
2. Em **Authorized JavaScript origins**, adicione `https://sistema-de-solicitacao.vercel.app`. Para testar uma prévia, adicione também a origem exata da URL de prévia da Vercel (somente `https://dominio`, sem caminho).
3. Na Vercel, adicione o ID público dessa credencial como `GOOGLE_CLIENT_ID` nos ambientes **Production** e **Preview**.
4. Configure `APP_SESSION_SECRET` como segredo com pelo menos 32 bytes aleatórios e faça um novo deploy.

O botão oficial do Google fornece um token de identidade. O servidor confirma a assinatura, a validade, o público e se o Gmail foi verificado. O site aceita somente endereços terminados em `@gmail.com` e usa o identificador estável `sub` do Google para reconhecer a conta.

Enquanto o aplicativo OAuth estiver no modo de teste, inclua cada conta permitida em **Test users**. Para liberar o acesso ao público, publique a tela de consentimento e conclua qualquer verificação de domínio solicitada pelo Google.

O acesso de demonstração, os dados do painel e o perfil institucional continuam vinculados ao navegador. As contas locais antigas continuam acessíveis da mesma forma. O token do Google nunca é salvo no armazenamento do navegador.

## Rodar localmente

Com Python 3.12 e um ambiente virtual ativo:

```sh
pip install -r requirements.txt
python app.py
```

Abra http://127.0.0.1:5000.
