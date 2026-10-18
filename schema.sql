
CREATE TABLE IF NOT EXISTS fornecedores (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    telefone VARCHAR(30) DEFAULT '',
    email VARCHAR(150) DEFAULT '',
    criado_em TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS produtos (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    categoria VARCHAR(100) DEFAULT '',
    preco NUMERIC(12,2) NOT NULL CHECK (preco >= 0),
    estoque INTEGER NOT NULL DEFAULT 0 CHECK (estoque >= 0),
    estoque_minimo INTEGER NOT NULL DEFAULT 5 CHECK (estoque_minimo >= 0),
    fornecedor_id BIGINT REFERENCES fornecedores(id)
        ON DELETE SET NULL,
    criado_em TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS movimentacoes (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tipo VARCHAR(10) NOT NULL
        CHECK (tipo IN ('compra', 'venda')),
    produto_id BIGINT NOT NULL REFERENCES produtos(id)
        ON DELETE RESTRICT,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    valor_unitario NUMERIC(12,2) NOT NULL
        CHECK (valor_unitario >= 0),
    total NUMERIC(14,2) GENERATED ALWAYS AS
        (quantidade * valor_unitario) STORED,
    criado_em TIMESTAMPTZ DEFAULT NOW()
);

CREATE OR REPLACE FUNCTION registrar_movimentacao(
    p_tipo TEXT,
    p_produto_id BIGINT,
    p_quantidade INTEGER,
    p_valor_unitario NUMERIC
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_estoque INTEGER;
    v_id BIGINT;
BEGIN
    IF p_tipo IS NULL
       OR p_tipo NOT IN ('compra', 'venda')
       OR p_quantidade IS NULL
       OR p_quantidade <= 0
       OR p_valor_unitario IS NULL
       OR p_valor_unitario < 0 THEN
        RAISE EXCEPTION 'Dados da movimentação inválidos';
    END IF;

    SELECT estoque INTO v_estoque
    FROM produtos
    WHERE id = p_produto_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Produto não encontrado';
    END IF;

    IF p_tipo = 'venda' AND v_estoque < p_quantidade THEN
        RAISE EXCEPTION 'Estoque insuficiente';
    END IF;

    UPDATE produtos
    SET estoque = estoque +
        CASE
            WHEN p_tipo = 'compra' THEN p_quantidade
            ELSE -p_quantidade
        END
    WHERE id = p_produto_id;

    INSERT INTO movimentacoes (
        tipo, produto_id, quantidade, valor_unitario
    )
    VALUES (
        p_tipo, p_produto_id, p_quantidade, p_valor_unitario
    )
    RETURNING id INTO v_id;

    RETURN v_id;
END;
$$;
