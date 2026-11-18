
// ==========================================
// SISTEMA DE REGISTRO DE SOLICITAÇÕES
// EQUIPE 5 - JAVASCRIPT E INTEGRAÇÃO
// ==========================================


// X - CONFIGURAÇÃO DA API PYTHON
// Os endereços serão preenchidos quando a Equipe 3 terminar.

const API = {
    cadastro: null,
    login: null
};


// X - FUNÇÃO PARA ENVIAR DADOS AO PYTHON

async function enviarParaAPI(endereco, dados) {

    if (!endereco) {
        alert("Backend ainda não conectado. Dados validados!");
        return null;
    }

    try {
        const resposta = await fetch(endereco, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(dados)
        });

        const resultado = await resposta.json();

        if (!resposta.ok) {
            throw new Error(resultado.mensagem || "Erro na solicitação.");
        }

        return resultado;

    } catch (erro) {
        alert("Não foi possível comunicar com o servidor.");
        console.error("Erro de comunicação:", erro);
        return null;
    }
}


// ==========================================
// X - SISTEMA DE CADASTRO
// ==========================================

const cadastroForm = document.getElementById("cadastroForm");

if (cadastroForm) {

    cadastroForm.addEventListener("submit", async function(event) {

        event.preventDefault();

        const nome = document.getElementById("nome").value.trim();
        const email = document.getElementById("email").value.trim();
        const usuario = document.getElementById("usuario").value.trim();
        const senha = document.getElementById("senha").value;
        const confirmar = document.getElementById("confirmar").value;

        if (!nome || !email || !usuario || !senha || !confirmar) {
            alert("Preencha todos os campos!");
            return;
        }

        if (senha !== confirmar) {
            alert("As senhas não são iguais!");
            return;
        }

        const dadosCadastro = {
            nome: nome,
            email: email,
            login: usuario,
            senha: senha
        };

        // X - ENVIO DO CADASTRO AO PYTHON

        const resultado = await enviarParaAPI(
            API.cadastro,
            dadosCadastro
        );

        if (resultado) {
            alert(resultado.mensagem || "Cadastro realizado!");
            cadastroForm.reset();
        }

    });
}


// ==========================================
// X - SISTEMA DE LOGIN
// ==========================================

const loginForm = document.getElementById("loginForm");

if (loginForm) {

    loginForm.addEventListener("submit", async function(event) {

        event.preventDefault();

        const usuario = document.getElementById("usuario").value.trim();
        const senha = document.getElementById("senha").value;

        if (!usuario || !senha) {
            alert("Preencha o login e a senha!");
            return;
        }

        const dadosLogin = {
            login: usuario,
            senha: senha
        };

        // X - ENVIO DO LOGIN AO PYTHON

        const resultado = await enviarParaAPI(
            API.login,
            dadosLogin
        );

        if (resultado) {
            alert(resultado.mensagem || "Login processado!");
        }

    });
}
