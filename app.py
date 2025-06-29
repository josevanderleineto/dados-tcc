import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
from collections import Counter

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard de Pesquisa - TCC",
    page_icon="📊",
    layout="wide"
)

# --- Conexão com o Banco de Dados ---
def init_connection():
    """Inicializa a conexão com o banco de dados PostgreSQL."""
    try:
        conn = psycopg2.connect(st.secrets["postgres"]["url"])
        return conn
    except (psycopg2.OperationalError, KeyError) as e:
        st.error(f"Não foi possível conectar ao banco de dados: {e}")
        return None

@st.cache_data(ttl=600)
def run_query(query):
    """Executa uma consulta e retorna os resultados como um DataFrame."""
    conn = init_connection()
    if conn:
        with conn:
            return pd.read_sql_query(query, conn)
    return pd.DataFrame()

# --- Carregamento dos Dados ---
df = run_query("SELECT * FROM respostas_questionario_quilombola;")

# --- Interface do Dashboard ---
st.title("📊 Dashboard de Análise da Pesquisa do TCC")
st.markdown("Visualização interativa das respostas do questionário sobre tecnologia e práticas leitoras.")

# --- Processamento e Exibição dos Gráficos ---
if df.empty:
    st.warning("Nenhum dado encontrado no banco de dados ou a conexão falhou. Verifique as configurações.")
else:
    # Define a ordem das respostas para os gráficos de frequência.
    ORDER_MAP = ["Nunca", "Raramente", "Ocasionalmente", "Frequentemente", "Muito frequentemente"]

    # Define as paletas de cores.
    GREEN_COLOR = "#2ca02c"
    QUALITATIVE_COLORS = px.colors.qualitative.D3
    BAR_COLOR_1 = px.colors.sequential.Purples[4]
    BAR_COLOR_2 = px.colors.sequential.Oranges[4]
    BAR_COLOR_3 = px.colors.sequential.Reds[4]
    BAR_COLOR_4 = px.colors.sequential.Blues[4]
    BAR_COLOR_5 = px.colors.sequential.Blues[6]

    # --- Seção: Perfil dos Participantes ---
    st.header("👤 Perfil dos Participantes")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Distribuição por Universidade")
        uni_counts = df['universidade'].value_counts().reset_index()
        uni_counts.columns = ['Universidade', 'Quantidade']
        fig_uni = px.bar(uni_counts, x='Universidade', y='Quantidade',
                         text='Quantidade', title="Respostas por Universidade",
                         color_discrete_sequence=[GREEN_COLOR])
        fig_uni.update_traces(textposition='outside')
        st.plotly_chart(fig_uni, use_container_width=True)

    with col2:
        st.subheader("Distribuição por Curso")
        df['curso_normalizado'] = df['curso'].astype(str).str.lower().str.strip().str.title()
        
        curso_counts = df['curso_normalizado'].value_counts().reset_index()
        curso_counts.columns = ['Curso', 'Quantidade']
        
        fig_curso = px.pie(curso_counts, names='Curso', values='Quantidade',
                           title="Respostas por Curso",
                           color_discrete_sequence=QUALITATIVE_COLORS)
        
        fig_curso.update_traces(textposition='outside',
                                textinfo='percent+label',
                                selector=dict(type='pie'))

        # ✅ Correção aplicada aqui
        fig_curso.update_layout(
            margin=dict(l=50, r=50, b=150, t=50),
            showlegend=False
        )
        
        st.plotly_chart(fig_curso, use_container_width=True)

    # --- Seção: Acesso à Leitura e Equipamentos ---
    st.header("📚 Acesso à Leitura e Equipamentos")
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Formas de Acesso à Leitura na Comunidade")
        acesso_list = [item.strip() for sublist in df['acesso_leitura_comunidade'].dropna().str.split(',') for item in sublist]
        acesso_counts = Counter(acesso_list)
        df_acesso = pd.DataFrame(acesso_counts.items(), columns=['Forma de Acesso', 'Quantidade']).sort_values('Quantidade', ascending=False)
        fig_acesso = px.bar(df_acesso, x='Forma de Acesso', y='Quantidade',
                            title="Como acessava o livro e a leitura na comunidade",
                            text='Quantidade', color_discrete_sequence=[BAR_COLOR_1])
        fig_acesso.update_traces(textposition='outside')
        st.plotly_chart(fig_acesso, use_container_width=True)

    with col4:
        st.subheader("Equipamentos Utilizados Antes da Universidade")
        equip_list = [item.strip() for sublist in df['equipamentos_utilizados'].dropna().str.split(',') for item in sublist]
        equip_counts = Counter(equip_list)
        df_equip = pd.DataFrame(equip_counts.items(), columns=['Equipamento', 'Quantidade']).sort_values('Quantidade', ascending=False)
        fig_equip = px.bar(df_equip, x='Equipamento', y='Quantidade',
                           title="Equipamentos utilizados para acessar leitura",
                           text='Quantidade', color_discrete_sequence=[BAR_COLOR_2])
        fig_equip.update_traces(textposition='outside')
        st.plotly_chart(fig_equip, use_container_width=True)

    # --- Seção: Acesso à Internet e Avaliações ---
    st.header("💻 Acesso à Internet e Avaliações")
    col5, col6 = st.columns(2)

    with col5:
        st.subheader("Qualidade do Acesso à Internet na Comunidade")
        internet_counts = df['acesso_internet_comunidade'].value_counts().reset_index()
        internet_counts.columns = ['Avaliação', 'Quantidade']
        fig_internet = px.funnel(internet_counts, x='Quantidade', y='Avaliação',
                                 title="Como é o acesso à internet na comunidade",
                                 color_discrete_sequence=[BAR_COLOR_3])
        st.plotly_chart(fig_internet, use_container_width=True)

    with col6:
        st.subheader("Avaliação dos Recursos Tecnológicos na Universidade")
        tec_uni_counts = df['avaliacao_tecnologia_universidade'].value_counts().reset_index()
        tec_uni_counts.columns = ['Avaliação', 'Quantidade']
        fig_tec_uni = px.bar(tec_uni_counts, y='Avaliação', x='Quantidade', orientation='h',
                             title="Avaliação dos recursos tecnológicos na universidade",
                             text='Quantidade', color_discrete_sequence=[BAR_COLOR_4])
        fig_tec_uni.update_traces(textposition='outside')
        st.plotly_chart(fig_tec_uni, use_container_width=True)

    # --- Seção: Frequência de Práticas Leitoras ---
    st.header("Frequência de Práticas Leitoras")

    st.subheader("Frequência de Acesso a Livros e Leitura (Pós-Universidade)")
    freq_acesso_counts = df['frequencia_acesso_geral'].value_counts().reindex(ORDER_MAP).fillna(0)
    fig_freq_acesso = px.bar(freq_acesso_counts, x=freq_acesso_counts.index, y=freq_acesso_counts.values,
                             labels={'x': 'Frequência', 'y': 'Quantidade'},
                             title="Frequência geral de acesso ao livro e leitura",
                             text=freq_acesso_counts.values, color_discrete_sequence=[BAR_COLOR_5])
    fig_freq_acesso.update_traces(textposition='outside')
    st.plotly_chart(fig_freq_acesso, use_container_width=True)

    st.subheader("Frequência de Leitura de Textos Longos (+20 páginas)")
    freq_longos_counts = df['frequencia_leitura_textos_longos'].value_counts().reindex(ORDER_MAP).fillna(0)
    fig_freq_longos = px.bar(freq_longos_counts, x=freq_longos_counts.index, y=freq_longos_counts.values,
                              labels={'x': 'Frequência', 'y': 'Quantidade'},
                              title="Frequência de leitura de textos longos",
                              color_discrete_sequence=[GREEN_COLOR])
    fig_freq_longos.update_traces(textposition='outside')
    st.plotly_chart(fig_freq_longos, use_container_width=True)

    # --- Seção: Respostas Descritivas ---
    st.header("📝 Respostas Descritivas")
    with st.expander("Ver justificativas sobre a leitura de textos longos"):
        justificativas = df['justificativa_leitura_longa'].dropna().tolist()
        for i, just in enumerate(justificativas):
            st.info(f"**Resposta {i+1}:** {just}")

    with st.expander("Ver experiências antes e depois da universidade"):
        experiencias = df['experiencia_antes_depois'].dropna().tolist()
        for i, exp in enumerate(experiencias):
            st.success(f"**Resposta {i+1}:** {exp}")

    # --- Seção: Raw Data ---
    st.header("📄 Tabela de Dados Brutos")
    with st.expander("Clique para ver a tabela de dados completa"):
        st.dataframe(df)
    # --- Seção: Média de Respostas por Comunidade ---
    st.header("🏘️ Média de Respostas por Comunidade")

    respostas_por_comunidade = df['comunidade_natal'].value_counts().reset_index()
    respostas_por_comunidade.columns = ['Comunidade', 'Total de Respostas']
    
    media_geral = respostas_por_comunidade['Total de Respostas'].mean()

    st.markdown(f"**Média geral de respostas por comunidade:** `{media_geral:.2f}`")

    st.dataframe(respostas_por_comunidade)
