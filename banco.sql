
USE sistema_solicitacoes;

CREATE TABLE IF NOT EXISTS comunicados (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(150) NOT NULL,
    mensagem TEXT NOT NULL,
    data VARCHAR(30),
    responsavel VARCHAR(150),
    status VARCHAR(30) DEFAULT 'Publicado'
);
