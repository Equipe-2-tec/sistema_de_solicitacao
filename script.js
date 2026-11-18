
// ==========================================
// CONFIGURACAO DA API PYTHON
// ==========================================

const API = {
    cadastro: "http://127.0.0.1:5000/cadastro",
    login: "http://127.0.0.1:5000/login",
    solicitacoes: "http://127.0.0.1:5000/solicitacoes"
};


// ==========================================
// FUNCAO DE COMUNICACAO COM A API
// ==========================================

async function enviarParaAPI(endereco, dados, metodo = "POST") {

    try {

        const resposta = await fetch(endereco, {
            method: metodo,
            headers: {
                "Content-Type": "application/json"
            },
            body: dados ? JSON.stringify(dados) : undefined
        });

        const resultado = await resposta.json();

        if (!resposta.ok) {
            throw new Error(
                resultado.erro || resultado.mensagem || "Erro na operação."
            );
        }

        return resultado;

    } catch (erro) {

        alert(erro.message || "Não foi possível comunicar com o servidor.");

        console.error("Erro:", erro);

        return null;
    }
}


// ==========================================
// SISTEMA DE CADASTRO
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

        const resultado = await enviarParaAPI(
            API.cadastro,
            dadosCadastro
        );

        if (resultado) {

            alert(resultado.mensagem);

            cadastroForm.reset();

            window.location.href = "index.html";
        }

    });
}


// ==========================================
// SISTEMA DE LOGIN
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

        const resultado = await enviarParaAPI(
            API.login,
            dadosLogin
        );

        if (resultado) {

            alert(resultado.mensagem);

            // Guarda o nome para identificar o usuário na interface.
            sessionStorage.setItem("usuarioNome", resultado.nome);
            sessionStorage.setItem("usuarioId", resultado.id);

            // Redirecionamento para a área do usuário.
            // Crie painel.html para essa página.
            window.location.href = "painel.html";
        }

    });
}


// ==========================================
// REGISTRAR SOLICITACAO
// ==========================================

async function registrarSolicitacao(nome, titulo, descricao) {

    return await enviarParaAPI(
        API.solicitacoes,
        {
            nome: nome,
            titulo: titulo,
            descricao: descricao
        }
    );
}


// ==========================================
// LISTAR SOLICITACOES
// ==========================================

async function listarSolicitacoes() {

    try {

        const resposta = await fetch(API.solicitacoes);

        if (!resposta.ok) {
            throw new Error("Erro ao listar solicitações.");
        }

        return await resposta.json();

    } catch (erro) {

        console.error(erro);
        alert("Não foi possível carregar as solicitações.");

        return null;
    }
}


// ==========================================
// ATUALIZAR STATUS
// ==========================================

async function atualizarStatus(id, status) {

    return await enviarParaAPI(
        `${API.solicitacoes}/${id}`,
        { status: status },
        "PUT"
    );
}


// ==========================================
// EXCLUIR SOLICITACAO
// ==========================================

async function excluirSolicitacao(id) {

    return await enviarParaAPI(
        `${API.solicitacoes}/${id}`,
        null,
        "DELETE"
    );
}
