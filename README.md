# Sistema de Registro de Solicitações

## Publicar na Vercel

1. Na Vercel, abra **Add New → Project** e importe o repositório atualizado do GitHub.
2. Use a raiz do repositório como **Root Directory** e **Flask** como **Framework Preset**. Deixe **Build Command** e **Output Directory** com os valores padrão.
3. Para gravar cadastros no MySQL, adicione `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD` e `MYSQL_DATABASE` em **Environment Variables**. Se usar o certificado CA do provedor, inclua o certificado público no projeto e configure `MYSQL_SSL_CA` com o caminho relativo à raiz.
4. Clique em **Deploy**. Abra a URL gerada para acessar o login e acrescente `/api/status` para verificar se a API responde. O status informa se o host do MySQL foi configurado. A conexão é usada ao gravar um cadastro.

O login de demonstração, as ocorrências e os comunicados usam o armazenamento do navegador. Use dados fictícios. A API de cadastro pode gravar o registro no MySQL quando o banco estiver configurado.

## Rodar localmente

Com Python 3.12 e um ambiente virtual ativo:

```sh
pip install -r requirements.txt
python app.py
```

Abra http://127.0.0.1:5000.
