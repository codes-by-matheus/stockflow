import streamlit as st
import pandas as pd
from database import cadastrar_produto, listar_produtos, criar_tabelas, registrar_movimentacao, listar_movimentacoes

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
# --- ABAS PRINCIPAIS ---
aba_produtos, aba_movimentacoes, aba_dashboard = st.tabs(["📋 Catálogo de Produtos", "🔄 Movimentações de Estoque", "📊 Dashboard & Alertas"])

with aba_produtos:
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


with aba_movimentacoes:
    st.subheader("🔄 Registrar Nova Movimentação")

    # Monta a lista de produtos para o operador escolher no menu
    # Exemplo de opção: "1 - PRD001 | Caixa de Papelão 50x50"
    dados_produtos = listar_produtos()
    opcoes_produtos = [f"{p[0]} - {p[1]} | {p[2]}" for p in dados_produtos]

    if not opcoes_produtos:
        st.warning("Cadastre produtos no catálogo antes de realizar movimentações.")
    else:
        with st.form("form_movimentacao", clear_on_submit=True):
            col_prod, col_tipo, col_qtd = st.columns([2, 1, 1])

            with col_prod:
                produto_selecionado = st.selectbox("Selecione o Produto", opcoes_produtos)

            with col_tipo:
                tipo_mov = st.radio("Tipo de Operação", ["SAIDA", "ENTRADA"], horizontal=True)

            with col_qtd:
                qtd_mov = st.number_input("Quantidade", min_value=1, step=1, value=1)

            obs_mov = st.text_input("Observação (Ex: Venda Pedido #102, NF #4500, Ajuste)")
            botao_confirmar = st.form_submit_button("Confirmar Movimentação")

            if botao_confirmar:
                # Pega o ID numérico do produto (que é o primeiro número antes do traço)
                produto_id = int(produto_selecionado.split(" - ")[0])

                sucesso, mensagem = registrar_movimentacao(produto_id, tipo_mov, int(qtd_mov), obs_mov)

                if sucesso:
                    st.success(mensagem)
                    st.rerun()
                else:
                    st.error(mensagem)

    st.divider()

    # --- HISTÓRICO DE MOVIMENTAÇÕES ---
    st.subheader("📜 Histórico de Movimentações")
    dados_mov = listar_movimentacoes()
    colunas_mov = ["ID", "Código", "Produto", "Tipo", "Quantidade", "Data e Hora", "Observação"]
    df_mov = pd.DataFrame(dados_mov, columns=colunas_mov)

    st.dataframe(df_mov, use_container_width=True)


with aba_dashboard:
    st.subheader("⚠️ Alertas de Reposição de Estoque")

    # Filtra produtos que atingiram ou estão abaixo do estoque mínimo
    df_alerta = df_produtos[df_produtos["Quantidade"] <= df_produtos["Estoque Mínimo"]]

    if df_alerta.empty:
        st.success("✅ Todos os produtos estão com níveis saudáveis de estoque!")
    else:
        st.error(f"🚨 Atenção: {len(df_alerta)} produto(s) precisam de reposição urgente!")
        # Mostra apenas as colunas mais importantes para a compra
        colunas_alerta = ["Código", "Nome", "Categoria", "Quantidade", "Estoque Mínimo"]
        st.dataframe(df_alerta[colunas_alerta], use_container_width=True)
        st.divider()
    st.subheader("📊 Indicadores Gráficos da Operação")

    # Cria duas colunas para colocar os gráficos lado a lado
    col_grafico1, col_grafico2 = st.columns(2)

    with col_grafico1:
        st.markdown("**📦 Peças em Estoque por Categoria**")
        qtd_por_categoria = df_produtos.groupby("Categoria")["Quantidade"].sum()
        st.bar_chart(qtd_por_categoria)

    with col_grafico2:
        st.markdown("**🔄 Volume de Peças: Entradas vs. Saídas**")
        dados_mov = listar_movimentacoes()
        if dados_mov:
            df_mov = pd.DataFrame(dados_mov, columns=["ID", "Código", "Produto", "Tipo", "Quantidade", "Data e Hora", "Observação"])
            mov_por_tipo = df_mov.groupby("Tipo")["Quantidade"].sum()
            st.bar_chart(mov_por_tipo)
        else:
            st.info("Ainda não há movimentações registradas.")