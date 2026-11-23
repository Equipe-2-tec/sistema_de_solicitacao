CREATE DATABASE IF NOT EXISTS sistema_solicitacoes
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE sistema_solicitacoes;


-- TABELA: usuarios
-- Armazena contas institucionais
-- 
CREATE TABLE usuarios (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome            VARCHAR(150)     NOT NULL,
    email           VARCHAR(180)     NOT NULL UNIQUE,   -- E-mail institucional
    senha_hash      VARCHAR(255)     NOT NULL,          -- Hash bcrypt/argon2
    tipo            ENUM('aluno','professor','funcionario','admin')
                                     NOT NULL DEFAULT 'aluno',
    matricula       VARCHAR(30)      UNIQUE,
    ativo           TINYINT(1)       NOT NULL DEFAULT 1,
    email_verificado TINYINT(1)      NOT NULL DEFAULT 0,
    criado_em       DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em   DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP
                                     ON UPDATE CURRENT_TIMESTAMP,
    ultimo_login    DATETIME         NULL,

    INDEX idx_usuarios_email (email),
    INDEX idx_usuarios_tipo  (tipo)
) ENGINE=InnoDB;

-- 
-- TABELA: sessoes
-- Controle de sessões de login
-- 
CREATE TABLE sessoes (
    id          CHAR(36)     PRIMARY KEY,          -- UUID
    usuario_id  INT UNSIGNED NOT NULL,
    token_hash  VARCHAR(255) NOT NULL,
    ip          VARCHAR(45)  NULL,
    user_agent  VARCHAR(255) NULL,
    criado_em   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expira_em   DATETIME     NOT NULL,
    ativo       TINYINT(1)   NOT NULL DEFAULT 1,

    CONSTRAINT fk_sessoes_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        ON DELETE CASCADE,

    INDEX idx_sessoes_usuario (usuario_id),
    INDEX idx_sessoes_expira  (expira_em)
) ENGINE=InnoDB;

-- 
-- TABELA: categorias
-- Categorias/tipos de solicitação
-- 
CREATE TABLE categorias (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome        VARCHAR(100) NOT NULL UNIQUE,
    descricao   VARCHAR(255) NULL,
    ativo       TINYINT(1)   NOT NULL DEFAULT 1,
    criado_em   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 
-- TABELA: solicitacoes
-- Registro principal das solicitações
-- 
CREATE TABLE solicitacoes (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    protocolo       VARCHAR(20)  NOT NULL UNIQUE,   -- Ex.: SOL-2025-000001
    usuario_id      INT UNSIGNED NOT NULL,          -- Quem abriu
    categoria_id    INT UNSIGNED NOT NULL,
    titulo          VARCHAR(150) NOT NULL,
    descricao       TEXT         NOT NULL,
    prioridade      ENUM('baixa','media','alta','urgente')
                                 NOT NULL DEFAULT 'media',
    status          ENUM('aberta','em_analise','em_andamento',
                         'aguardando_usuario','resolvida','cancelada')
                                 NOT NULL DEFAULT 'aberta',
    responsavel_id  INT UNSIGNED NULL,              -- Quem atende
    resposta        TEXT         NULL,
    criado_em       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
                                 ON UPDATE CURRENT_TIMESTAMP,
    resolvido_em    DATETIME     NULL,

    CONSTRAINT fk_solic_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_solic_categoria
        FOREIGN KEY (categoria_id) REFERENCES categorias(id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_solic_responsavel
        FOREIGN KEY (responsavel_id) REFERENCES usuarios(id)
        ON DELETE SET NULL,

    INDEX idx_solic_status      (status),
    INDEX idx_solic_usuario     (usuario_id),
    INDEX idx_solic_categoria   (categoria_id),
    INDEX idx_solic_criado_em   (criado_em)
) ENGINE=InnoDB;

-- 
-- TABELA: solicitacao_historico
-- Auditoria / andamento das solicitações
-- 
CREATE TABLE solicitacao_historico (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    solicitacao_id  INT UNSIGNED NOT NULL,
    usuario_id      INT UNSIGNED NULL,          -- Quem alterou
    status_anterior ENUM('aberta','em_analise','em_andamento',
                         'aguardando_usuario','resolvida','cancelada') NULL,
    status_novo     ENUM('aberta','em_analise','em_andamento',
                         'aguardando_usuario','resolvida','cancelada') NOT NULL,
    comentario      TEXT NULL,
    criado_em       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_hist_solic
        FOREIGN KEY (solicitacao_id) REFERENCES solicitacoes(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_hist_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        ON DELETE SET NULL,

    INDEX idx_hist_solic (solicitacao_id)
) ENGINE=InnoDB;

 ============================================
 TABELA: anexos
 Arquivos vinculados a solicitações
 
CREATE TABLE anexos (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    solicitacao_id  INT UNSIGNED NOT NULL,
    nome_original   VARCHAR(255) NOT NULL,
    nome_arquivo    VARCHAR(255) NOT NULL,     -- Nome salvo no servidor
    caminho         VARCHAR(500) NOT NULL,
    mime_type       VARCHAR(100) NOT NULL,
    tamanho_bytes   INT UNSIGNED NOT NULL,
    criado_em       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_anexos_solic
        FOREIGN KEY (solicitacao_id) REFERENCES solicitacoes(id)
        ON DELETE CASCADE,

    INDEX idx_anexos_solic (solicitacao_id)
) ENGINE=InnoDB;

 
-- TABELA: recuperacao_senha
-- Tokens de "Esqueci minha senha"
-- 
CREATE TABLE recuperacao_senha (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    usuario_id  INT UNSIGNED NOT NULL,
    token_hash  VARCHAR(255) NOT NULL,
    ip          VARCHAR(45)  NULL,
    usado       TINYINT(1)   NOT NULL DEFAULT 0,
    criado_em   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expira_em   DATETIME     NOT NULL,

    CONSTRAINT fk_recc_senha_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        ON DELETE CASCADE,

    INDEX idx_rec_senha_usuario (usuario_id),
    INDEX idx_rec_senha_token   (token_hash)
) ENGINE=InnoDB;

-- 
-- TABELA: tentativas_login
-- Proteção contra força bruta
-- 
CREATE TABLE tentativas_login (
    id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    email       VARCHAR(180) NOT NULL,
    ip          VARCHAR(45)  NOT NULL,
    sucesso     TINYINT(1)   NOT NULL DEFAULT 0,
    criado_em   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_tent_email (email),
    INDEX idx_tent_ip    (ip),
    INDEX idx_tent_data  (criado_em)
) ENGINE=InnoDB;

-- 
-- TABELA: logs_auditoria
-- Registro geral de ações
-- 
CREATE TABLE logs_auditoria (
    id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    usuario_id  INT UNSIGNED NULL,
    acao        VARCHAR(100) NOT NULL,   -- ex.: 'LOGIN', 'CRIAR_SOLICITACAO'
    entidade    VARCHAR(50)  NULL,       -- ex.: 'solicitacoes'
    entidade_id INT UNSIGNED NULL,
    detalhes    JSON         NULL,
    ip          VARCHAR(45)  NULL,
    criado_em   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_log_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        ON DELETE SET NULL,

    INDEX idx_log_usuario (usuario_id),
    INDEX idx_log_data    (criado_em)
) ENGINE=InnoDB;
