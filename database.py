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


if __name__ == "__main__":
    criar_tabelas()
    print("Tabelas verificadas com sucesso!")

    # 1. Verifica se já tem produtos
    produtos_atuais = listar_produtos()

    # 2. Se não tiver nenhum, cadastra um produto de teste
    if not produtos_atuais:
        print("Cadastrando produto de teste...")
        cadastrar_produto("PRD001", "Caixa de Papelão 50x50", "Embalagens", 100, 4.50, 20)

    # 3. Lista e mostra o que tem no banco
    print("Produtos no estoque:")
    for item in listar_produtos():
        print(item)