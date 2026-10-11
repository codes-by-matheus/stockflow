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


if __name__ == "__main__":
    criar_tabelas()
    print("Banco de dados e tabelas criados com sucesso!")