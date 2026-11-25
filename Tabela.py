
CREATE TABLE ocorrencias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    protocolo VARCHAR(20) NOT NULL UNIQUE,
    local VARCHAR(100) NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    titulo VARCHAR(150) NOT NULL,
    descricao TEXT NOT NULL,
    anexos TEXT,
    data VARCHAR(30),
    situacao VARCHAR(50) DEFAULT 'Pendente'
);
