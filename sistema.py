CREATE DATABASE sistema_solicitacoes;

USE sistema_solicitacoes;

CREATE TABLE solicitacoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    titulo VARCHAR(150) NOT NULL,
    descricao TEXT NOT NULL,
    status VARCHAR(30) DEFAULT 'Pendente'
)