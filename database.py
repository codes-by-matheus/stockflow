import sqlite3

def conectar_banco():
    conexao = sqlite3.connect("stockflow.db")
    conexao.execute("PRAGMA foreign_keys = ON;")
    return conexao


def criar_tabelas():
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL,
            quantidade INTEGER NOT NULL DEFAULT 0,
            preco REAL NOT NULL DEFAULT 0.0,
            estoque_minimo INTEGER NOT NULL DEFAULT 5
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL,
            tipo TEXT NOT NULL CHECK(tipo IN ('ENTRADA', 'SAIDA')),
            quantidade INTEGER NOT NULL CHECK(quantidade > 0),
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            observacao TEXT,
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        );
    """)

    conexao.commit()
    conexao.close()


def cadastrar_produto(codigo, nome, categoria, quantidade, preco, estoque_minimo):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO produtos (codigo, nome, categoria, quantidade, preco, estoque_minimo)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (codigo, nome, categoria, quantidade, preco, estoque_minimo))

    conexao.commit()
    conexao.close()


def listar_produtos():
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()

    conexao.close()
    return produtos


def registrar_movimentacao(produto_id, tipo, quantidade, observacao=""):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    # 1. Busca a quantidade atual do produto
    cursor.execute("SELECT quantidade FROM produtos WHERE id = ?", (produto_id,))
    resultado = cursor.fetchone()

    # Se o produto não existir no banco
    if not resultado:
        conexao.close()
        return False, "Produto não encontrado!"

    saldo_atual = resultado[0]


            # 2. Verifica a regra de negócio e calcula o novo saldo
    if tipo == "SAIDA":
        if quantidade > saldo_atual:
            conexao.close()
            return False, f"Saldo insuficiente! Estoque atual: {saldo_atual}"
        novo_saldo = saldo_atual - quantidade

    elif tipo == "ENTRADA":
        novo_saldo = saldo_atual + quantidade

    else:
        conexao.close()
        return False, "Tipo de movimentação inválido! Use 'ENTRADA' ou 'SAIDA'."

    # 3. Atualiza o saldo do produto na tabela 'produtos'
    cursor.execute("""
        UPDATE produtos SET quantidade = ? WHERE id = ?
    """, (novo_saldo, produto_id))

    # 4. Grava o registro no histórico da tabela 'movimentacoes'
    cursor.execute("""
        INSERT INTO movimentacoes (produto_id, tipo, quantidade, observacao)
        VALUES (?, ?, ?, ?)
    """, (produto_id, tipo, quantidade, observacao))

        # 5. Salva em definitivo e fecha
    conexao.commit()
    conexao.close()
    return True, f"Movimentação de {tipo} realizada com sucesso!"


def listar_movimentacoes():
    conexao = conectar_banco()
    cursor = conexao.cursor()

    # O JOIN junta as duas tabelas para trazer o código e o nome do produto!
    cursor.execute("""
        SELECT 
            m.id,
            p.codigo,
            p.nome,
            m.tipo,
            m.quantidade,
            m.data_hora,
            m.observacao
        FROM movimentacoes m
        JOIN produtos p ON m.produto_id = p.id
        ORDER BY m.id DESC
    """)
    movimentacoes = cursor.fetchall()

    conexao.close()
    return movimentacoes


if __name__ == "__main__":
    criar_tabelas()

    print("\n--- TESTE 1: Saída permitida ---")
    sucesso, msg = registrar_movimentacao(1, "SAIDA", 20, "Venda Pedido #101")
    print(msg)

    print("\n--- TESTE 2: Tentativa de saída maior que o estoque ---")
    sucesso, msg = registrar_movimentacao(1, "SAIDA", 500, "Tentativa sem estoque")
    print(msg)

    print("\n--- TESTE 3: Entrada de mercadoria ---")
    sucesso, msg = registrar_movimentacao(1, "ENTRADA", 30, "Chegada NF #5050")
    print(msg)

    print("\n--- SALDO FINAL DOS PRODUTOS ---")
    for item in listar_produtos():
        print(item)