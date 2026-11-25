
document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const dados = {
        school: document.getElementById('school').value,
        email: document.getElementById('regEmail').value,
        owner: document.getElementById('owner').value,
        password: document.getElementById('regPass').value,
        confirm: document.getElementById('regConfirm').value
    };

    const mensagem = document.getElementById('registerMsg');

    try {
        const resposta = await fetch('/cadastro-institucional', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dados)
        });

        const resultado = await resposta.json();

        mensagem.textContent =
            resultado.mensagem || resultado.erro;

        if (resposta.ok) {
            document.getElementById('registerForm').reset();
        }

    } catch (erro) {
        mensagem.textContent = 'Erro ao conectar ao servidor.';
    }
});
