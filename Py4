
document.getElementById('recoverForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const email = document.getElementById('recoverEmail').value;
    const mensagem = document.getElementById('recoverMsg');

    try {
        const resposta = await fetch('/recuperar-senha', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email: email })
        });

        const dados = await resposta.json();

        mensagem.textContent = dados.mensagem || dados.erro;

    } catch (erro) {
        mensagem.textContent = 'Erro ao conectar ao servidor.';
    }
});
