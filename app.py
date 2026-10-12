import streamlit as st
import pandas as pd
from database import cadastrar_produto, listar_produtos, criar_tabelas

# Garante que as tabelas existem ao iniciar
criar_tabelas()

# Configuração da página web
st.set_page_config(page_title="StockFlow", layout="wide")
st.title("📦 StockFlow — Gestão de Estoque")
# --- BARRA LATERAL: Formulário de Cadastro ---
with st.sidebar.form("form_novo_produto", clear_on_submit=True):
    st.subheader("➕ Cadastrar Novo Produto")
    
    codigo = st.text_input("Código do Produto (SKU) *")
    nome = st.text_input("Nome do Produto *")
    categoria = st.selectbox("Categoria", ["Embalagens", "Ferramentas", "Eletrônicos", "Segurança", "Armazenagem", "Outros"])
    quantidade = st.number_input("Quantidade Inicial", min_value=0, step=1, value=0)
    preco = st.number_input("Preço Unitário (R$)", min_value=0.0, step=0.10, format="%.2f")
    estoque_minimo = st.number_input("Estoque Mínimo de Alerta", min_value=1, step=1, value=5)

    botao_salvar = st.form_submit_button("Salvar Produto")

    if botao_salvar:
        if not codigo or not nome:
            st.error("Por favor, preencha o Código e o Nome do produto.")
        else:
            try:
                cadastrar_produto(codigo, nome, categoria, int(quantidade), float(preco), int(estoque_minimo))
                st.success(f"Produto '{nome}' cadastrado com sucesso!")
                st.rerun()
            except Exception:
                st.error("Erro: Já existe um produto cadastrado com esse código!")
# --- CARDS DE INDICADORES (KPIs) ---
dados_produtos = listar_produtos()
colunas = ["ID", "Código", "Nome", "Categoria", "Quantidade", "Preço (R$)", "Estoque Mínimo"]
df_produtos = pd.DataFrame(dados_produtos, columns=colunas)

# Cálculos rápidos
total_produtos = len(df_produtos)
total_itens_fisicos = int(df_produtos["Quantidade"].sum()) if not df_produtos.empty else 0
valor_total_estoque = float((df_produtos["Quantidade"] * df_produtos["Preço (R$)"]).sum()) if not df_produtos.empty else 0.0

# 3 Colunas de métricas visuais
m1, m2, m3 = st.columns(3)
m1.metric("📦 Produtos Cadastrados", total_produtos)
m2.metric("🔢 Total de Peças Físicas", f"{total_itens_fisicos:,}".replace(",", "."))
m3.metric("💰 Valor Total do Estoque", f"R$ {valor_total_estoque:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

st.divider() # Uma linha divisória elegante
# Subtítulo da seção
st.subheader("📋 Catálogo de Produtos")

# Busca os produtos do banco e monta o DataFrame inicial
dados_produtos = listar_produtos()
colunas = ["ID", "Código", "Nome", "Categoria", "Quantidade", "Preço (R$)", "Estoque Mínimo"]
df_produtos = pd.DataFrame(dados_produtos, columns=colunas)

# --- FILTROS DE PESQUISA ---
col1, col2 = st.columns([2, 1])

with col1:
    termo_busca = st.text_input("🔍 Pesquisar por Código ou Nome", placeholder="Digite para buscar...")

with col2:
    # Pega as categorias existentes no banco e adiciona a opção "Todas"
    categorias_disponiveis = ["Todas"] + sorted(df_produtos["Categoria"].unique().tolist())
    categoria_selecionada = st.selectbox("Filtrar por Categoria", categorias_disponiveis)

# Aplica os filtros no DataFrame
df_filtrado = df_produtos.copy()

if termo_busca:
    for palavra in termo_busca.split():
        df_filtrado = df_filtrado[
            df_filtrado["Nome"].str.contains(palavra, case=False, na=False) |
            df_filtrado["Código"].str.contains(palavra, case=False, na=False)
        ]

if categoria_selecionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Categoria"] == categoria_selecionada]

# Mostra a tabela filtrada
st.dataframe(df_filtrado, use_container_width=True)