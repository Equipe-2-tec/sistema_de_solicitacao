
USE sistema_solicitacoes;

ALTER TABLE ocorrencias
ADD COLUMN prioridade VARCHAR(30) DEFAULT 'Média',
ADD COLUMN providencias TEXT,
ADD COLUMN justificativa TEXT;

CREATE TABLE IF NOT EXISTS historico_ocorrencias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    protocolo VARCHAR(20) NOT NULL,
    campo VARCHAR(50) NOT NULL,
    valor_anterior TEXT,
    valor_novo TEXT,
    responsavel VARCHAR(150),
    data VARCHAR(30)
);
