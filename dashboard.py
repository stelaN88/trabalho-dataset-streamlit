import streamlit as st
import pandas as pd
import plotly.express as px

px.defaults.template = "plotly_white"

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==========================================

st.set_page_config(
    page_title="Online Retail | Dashboard",
    page_icon="📊",
    layout="wide"
)

# ==========================================
# 2. PERSONALIZAÇÃO VISUAL
# ==========================================

st.markdown("""

<style>
    /* FUNDO PRINCIPAL */
    .stApp {
        background-color: #F4F7FB !important;
    }

    /* BARRA LATERAL */
    [data-testid="stSidebar"] {
        background-color: #E8EFF8 !important;
    }

    /* TODOS OS TEXTOS */
    .stApp,
    .stApp p,
    .stApp label,
    .stApp span,
    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp h4,
    [data-testid="stSidebar"] * {
        color: #000000 !important;
    }

    /* TÍTULO PRINCIPAL */
    .main-title {
        color: #000000 !important;
        font-size: 34px;
        font-weight: 700;
        margin-bottom: 0;
    }

    /* SUBTÍTULO */
    .subtitle {
        color: #000000 !important;
        font-size: 15px;
        margin-bottom: 25px;
    }

    /* CARTÕES DOS INDICADORES */
    [data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        border: 1px solid #D5DFEA;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.04);
    }

    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"] {
        color: #000000 !important;
    }

    /* TABELA */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
    }

    /* Forçar somente a cor da escrita do campo de data */
    [data-testid="stDateInput"] input,
    [data-testid="stDateInput"] input::placeholder,
    [data-testid="stDateInput"] div,
    [data-testid="stDateInput"] span {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    }

    /* Ícone do calendário */
    [data-testid="stDateInput"] button {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }

    [data-testid="stDateInput"] button svg {
        fill: #000000 !important;
        color: #000000 !important;
        stroke: #000000 !important;
    }

   /* TEXTO DO PAÍS NO SELECTBOX FECHADO */
    [data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] [role="combobox"] {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }

    [data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] [role="combobox"] > div {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }

    /* TEXTO INTERNO DO VALOR SELECIONADO */
    [data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] [aria-selected="true"] {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }
</style>

""", unsafe_allow_html=True)

# ==========================================
# 3. CARREGAMENTO DOS DADOS
# ==========================================

@st.cache_data
def carregar_dados():
    dados = pd.read_csv("dados/online_retail_vendas.csv")
    dados["InvoiceDate"] = pd.to_datetime(dados["InvoiceDate"])
    return dados

df = carregar_dados()

# ==========================================
# 4. CABEÇALHO
# ==========================================

st.markdown(
    '<p class="main-title">📊 Online Retail Dashboard</p>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="subtitle">Painel interativo de análise de vendas e desempenho comercial.</p>',
    unsafe_allow_html=True
)

st.divider()

# ==========================================
# 5. FILTROS
# ==========================================

st.sidebar.title("🔎 Filtros")

st.sidebar.caption(
    "Utilize os filtros abaixo para personalizar a análise."
)

data_inicial = df["InvoiceDate"].min().date()
data_final = df["InvoiceDate"].max().date()

periodo = st.sidebar.date_input(
    "Período das vendas",
    value=(data_inicial, data_final),
    min_value=data_inicial,
    max_value=data_final
)

paises = sorted(df["Country"].dropna().unique())

pais_selecionado = st.sidebar.selectbox(
    "País",
    ["Todos"] + paises
)

st.sidebar.divider()

st.sidebar.caption(
    "Fonte: UCI Machine Learning Repository"
)

# ==========================================
# 6. APLICAÇÃO DOS FILTROS
# ==========================================

df_filtrado = df.copy()

if len(periodo) == 2:
    inicio, fim = periodo
    df_filtrado = df_filtrado[
        (df_filtrado["InvoiceDate"].dt.date >= inicio) &
        (df_filtrado["InvoiceDate"].dt.date <= fim)
    ]

if pais_selecionado != "Todos":
    df_filtrado = df_filtrado[
        df_filtrado["Country"] == pais_selecionado
    ]

# ==========================================
# 7. VERIFICAÇÃO DOS RESULTADOS
# ==========================================

if df_filtrado.empty:
    st.warning("Não existem vendas para os filtros selecionados.")
    st.stop()

# ==========================================
# 8. CÁLCULO DOS INDICADORES
# ==========================================

faturamento = df_filtrado["TotalPrice"].sum()

quantidade_pedidos = df_filtrado["InvoiceNo"].nunique()

ticket_medio = (
    df_filtrado.groupby("InvoiceNo")["TotalPrice"]
    .sum()
    .mean()
)

# ==========================================
# 9. INDICADORES PRINCIPAIS
# ==========================================

st.subheader("Indicadores gerais")

col1, col2, col3 = st.columns(3)

col1.metric(
    label="💰 Faturamento total",
    value=f"£ {faturamento:,.2f}"
)

col2.metric(
    label="🛒 Quantidade de pedidos",
    value=f"{quantidade_pedidos:,}"
)

col3.metric(
    label="📈 Ticket médio",
    value=f"£ {ticket_medio:,.2f}"
)

st.caption(
    f"Exibindo informações de {len(df_filtrado):,} registros."
)

st.divider()

# ==========================================
# 10. FATURAMENTO MENSAL
# ==========================================

st.subheader("Evolução do faturamento")

faturamento_mensal = (
    df_filtrado.assign(
        Mes=df_filtrado["InvoiceDate"].dt.to_period("M").astype(str)
    )
    .groupby("Mes")["TotalPrice"]
    .sum()
    .reset_index()
)

grafico_faturamento = px.bar(
    faturamento_mensal,
    x="Mes",
    y="TotalPrice",
    title="Faturamento mensal",
    labels={"Mes": "Mês", "TotalPrice": "Faturamento (£)"}
)
st.plotly_chart(grafico_faturamento, use_container_width=True)

st.divider()

# ==========================================
# 11. PRODUTOS E PAÍSES
# ==========================================

coluna1, coluna2 = st.columns(2)

with coluna1:

    st.subheader("🏆 Produtos mais vendidos")

    produtos = (
        df_filtrado.groupby("Description")["Quantity"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .sort_values()
    )

    grafico_produtos = px.bar(
        produtos.reset_index(),
        x="Quantity",
        y="Description",
        orientation="h",
        title="Produtos mais vendidos",
        labels={"Quantity": "Quantidade vendida", "Description": "Produto"}
    )
    st.plotly_chart(grafico_produtos, use_container_width=True)

with coluna2:

    st.subheader("🌎 Faturamento por país")

    faturamento_pais = (
        df_filtrado.groupby("Country")["TotalPrice"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .sort_values()
    )

    grafico_paises = px.bar(
        faturamento_pais.reset_index(),
        x="TotalPrice",
        y="Country",
        orientation="h",
        title="Faturamento por país",
        labels={"TotalPrice": "Faturamento (£)", "Country": "País"}
    )
    st.plotly_chart(grafico_paises, use_container_width=True)

st.divider()

# ==========================================
# 12. ANÁLISES COMPLEMENTARES
# ==========================================

# Reutiliza os indicadores mensais analisados no notebook.
resumo_mensal = (
    df_filtrado.assign(
        Mes=df_filtrado["InvoiceDate"].dt.to_period("M").astype(str)
    )
    .groupby("Mes")
    .agg(
        Faturamento=("TotalPrice", "sum"),
        QuantidadePedidos=("InvoiceNo", "nunique")
    )
    .reset_index()
)
resumo_mensal["TicketMedio"] = (
    resumo_mensal["Faturamento"] / resumo_mensal["QuantidadePedidos"]
)

coluna3, coluna4 = st.columns(2)

with coluna3:
    st.subheader("🛒 Pedidos por mês")

    grafico_pedidos = px.line(
        resumo_mensal,
        x="Mes",
        y="QuantidadePedidos",
        markers=True,
        title="Quantidade de pedidos por mês",
        labels={"Mes": "Mês", "QuantidadePedidos": "Quantidade de pedidos"}
    )
    st.plotly_chart(grafico_pedidos, use_container_width=True)
    mes_mais_pedidos = resumo_mensal.loc[
        resumo_mensal["QuantidadePedidos"].idxmax()
    ]
    st.caption(
        f"No recorte selecionado, {mes_mais_pedidos['Mes']} teve a maior "
        f"quantidade de pedidos: {int(mes_mais_pedidos['QuantidadePedidos']):,}."
    )

with coluna4:
    st.subheader("💰 Distribuição do valor dos pedidos")

    # Cada observação do histograma corresponde a um pedido completo.
    valores_pedidos = (
        df_filtrado.groupby("InvoiceNo")["TotalPrice"]
        .sum()
        .reset_index(name="ValorPedido")
    )
    grafico_distribuicao = px.histogram(
        valores_pedidos,
        x="ValorPedido",
        nbins=40,
        title="Distribuição do valor dos pedidos",
        labels={"ValorPedido": "Valor do pedido (£)"}
    )
    grafico_distribuicao.update_layout(yaxis_title="Quantidade de pedidos")
    st.plotly_chart(grafico_distribuicao, use_container_width=True)
    st.caption(
        f"Mediana dos pedidos selecionados: "
        f"£ {valores_pedidos['ValorPedido'].median():,.2f}. "
        "Todos os pedidos foram mantidos, inclusive os de valor elevado."
    )

st.subheader("📈 Quantidade de pedidos e ticket médio")

grafico_relacao = px.scatter(
    resumo_mensal,
    x="QuantidadePedidos",
    y="TicketMedio",
    hover_name="Mes",
    title="Quantidade de pedidos × ticket médio mensal",
    labels={
        "QuantidadePedidos": "Quantidade de pedidos",
        "TicketMedio": "Ticket médio (£)"
    }
)
st.plotly_chart(grafico_relacao, use_container_width=True)
st.caption(
    "Cada ponto representa um mês do período selecionado. "
    "O gráfico permite comparar volume de pedidos e valor médio; "
    "a posição dos pontos não demonstra uma relação de causa e efeito. "
    "Meses parcialmente incluídos no período exigem cuidado na comparação."
)

st.divider()

# ==========================================
# 13. TABELA DE DADOS
# ==========================================

with st.expander("📋 Consultar dados das vendas"):

    st.write(
        f"Total de registros encontrados: {len(df_filtrado):,}"
    )

    st.dataframe(
        df_filtrado,
        use_container_width=True,
        hide_index=True
    )

# ==========================================
# 14. RODAPÉ
# ==========================================

st.divider()

st.caption(
    "Projeto acadêmico de Análise de Dados | "
    "Dataset: Online Retail | Fonte: UCI Repository"
)
