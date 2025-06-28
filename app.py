import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
from collections import Counter

# --- Configuração da Página ---
# Define o layout da página para ser "wide" (largo), o título e o ícone.
st.set_page_config(
    page_title="Dashboard de Pesquisa - TCC",
    page_icon="📊",
    layout="wide"
)

# --- Conexão com o Banco de Dados ---
# A função init_connection inicializa a conexão com o banco de dados PostgreSQL
# usando a URL de conexão armazenada nos segredos do Streamlit.
def init_connection():
    """Inicializa a conexão com o banco de dados PostgreSQL."""
    # Tenta conectar usando a URL fornecida nos segredos.
    try:
        conn = psycopg2.connect(st.secrets["postgres"]["url"])
        return conn
    # Se a conexão falhar, exibe uma mensagem de erro.
    except (psycopg2.OperationalError, KeyError) as e:
        st.error(f"Não foi possível conectar ao banco de dados: {e}")
        return None

# A função run_query executa uma consulta SQL e retorna os resultados como um DataFrame do Pandas.
# O decorador @st.cache_data garante que a consulta seja executada apenas uma vez,
# a menos que a consulta ou os parâmetros mudem, melhorando o desempenho.
@st.cache_data(ttl=600)
def run_query(query):
    """Executa uma consulta e retorna os resultados como um DataFrame."""
    # Conecta ao banco de dados.
    conn = init_connection()
    if conn:
        # Usa um bloco 'with' para garantir que a conexão seja fechada corretamente.
        with conn:
            # Retorna os resultados da consulta como um DataFrame do Pandas.
            return pd.read_sql_query(query, conn)
    # Retorna um DataFrame vazio se a conexão falhar.
    return pd.DataFrame()

# --- Carregamento dos Dados ---
# Carrega todos os dados da tabela do questionário.
df = run_query("SELECT * FROM respostas_questionario_quilombola;")

# --- Interface do Dashboard ---
# Título principal do dashboard.
st.title("📊 Dashboard de Análise da Pesquisa do TCC")
st.markdown("Visualização interativa das respostas do questionário sobre tecnologia e práticas leitoras.")

# --- Processamento e Exibição dos Gráficos ---
# Verifica se o DataFrame não está vazio antes de tentar criar os gráficos.
if df.empty:
    st.warning("Nenhum dado encontrado no banco de dados ou a conexão falhou. Verifique as configurações.")
else:
    # Define a ordem das respostas para os gráficos de frequência.
    ORDER_MAP = ["Nunca", "Raramente", "Ocasionalmente", "Frequentemente", "Muito frequentemente"]

    # Define as novas cores para os gráficos para maior contraste
    # Exemplo de paleta:
    # PRIMARY_COLOR para gráficos de barra única
    PRIMARY_COLOR = "#2ca02c" # Um verde vibrante
    # SECONDARY_COLORS para gráficos com múltiplas categorias (pizza, barras com muitas categorias)
    SECONDARY_COLORS = px.colors.qualitative.D3 # Uma paleta qualitativa com cores distintas

    # --- Seção: Perfil dos Participantes ---
    st.header("👤 Perfil dos Participantes")
    col1, col2 = st.columns(2) # Cria duas colunas para organizar os gráficos.

    with col1:
        # Gráfico de distribuição por universidade.
        st.subheader("Distribuição por Universidade")
        # Conta as ocorrências de cada universidade.
        uni_counts = df['universidade'].value_counts().reset_index()
        uni_counts.columns = ['Universidade', 'Quantidade']
        # Cria um gráfico de barras.
        fig_uni = px.bar(uni_counts, x='Universidade', y='Quantidade',
                         text='Quantidade', title="Respostas por Universidade",
                         color_discrete_sequence=[PRIMARY_COLOR])
        fig_uni.update_traces(textposition='outside')
        st.plotly_chart(fig_uni, use_container_width=True)

    with col2:
        # Gráfico de distribuição por curso.
        st.subheader("Distribuição por Curso")
        # Conta as ocorrências de cada curso.
        curso_counts = df['curso'].value_counts().reset_index()
        curso_counts.columns = ['Curso', 'Quantidade']
        # Cria um gráfico de pizza.
        fig_curso = px.pie(curso_counts, names='Curso', values='Quantidade',
                           title="Respostas por Curso",
                           color_discrete_sequence=SECONDARY_COLORS) # Usando a nova paleta secundária
        st.plotly_chart(fig_curso, use_container_width=True)

    # --- Seção: Acesso à Leitura e Equipamentos ---
    st.header("📚 Acesso à Leitura e Equipamentos")
    col3, col4 = st.columns(2)

    with col3:
        # Gráfico das formas de acesso à leitura na comunidade.
        st.subheader("Formas de Acesso à Leitura na Comunidade")
        # Processa a coluna de acesso à leitura, que contém múltiplos valores separados por vírgula.
        acesso_list = [item.strip() for sublist in df['acesso_leitura_comunidade'].dropna().str.split(',') for item in sublist]
        acesso_counts = Counter(acesso_list)
        # Converte o contador para um DataFrame.
        df_acesso = pd.DataFrame(acesso_counts.items(), columns=['Forma de Acesso', 'Quantidade']).sort_values('Quantidade', ascending=False)
        # Cria um gráfico de barras.
        fig_acesso = px.bar(df_acesso, x='Forma de Acesso', y='Quantidade',
                            title="Como acessava o livro e a leitura na comunidade",
                            text='Quantidade', color_discrete_sequence=[PRIMARY_COLOR])
        st.plotly_chart(fig_acesso, use_container_width=True)

    with col4:
        # Gráfico dos equipamentos utilizados antes da universidade.
        st.subheader("Equipamentos Utilizados Antes da Universidade")
        # Processa a coluna de equipamentos, similar à de acesso à leitura.
        equip_list = [item.strip() for sublist in df['equipamentos_utilizados'].dropna().str.split(',') for item in sublist]
        equip_counts = Counter(equip_list)
        # Converte o contador para um DataFrame.
        df_equip = pd.DataFrame(equip_counts.items(), columns=['Equipamento', 'Quantidade']).sort_values('Quantidade', ascending=False)
        # Cria um gráfico de barras.
        fig_equip = px.bar(df_equip, x='Equipamento', y='Quantidade',
                           title="Equipamentos utilizados para acessar leitura",
                           text='Quantidade', color_discrete_sequence=[PRIMARY_COLOR])
        st.plotly_chart(fig_equip, use_container_width=True)

    # --- Seção: Acesso à Internet e Avaliações ---
    st.header("💻 Acesso à Internet e Avaliações")
    col5, col6 = st.columns(2)

    with col5:
        # Gráfico da qualidade do acesso à internet na comunidade.
        st.subheader("Qualidade do Acesso à Internet na Comunidade")
        internet_counts = df['acesso_internet_comunidade'].value_counts().reset_index()
        internet_counts.columns = ['Avaliação', 'Quantidade']
        # Cria um gráfico de funil.
        fig_internet = px.funnel(internet_counts, x='Quantidade', y='Avaliação',
                                 title="Como é o acesso à internet na comunidade",
                                 color_discrete_sequence=[PRIMARY_COLOR])
        st.plotly_chart(fig_internet, use_container_width=True)

    with col6:
        # Gráfico da avaliação dos recursos tecnológicos na universidade.
        st.subheader("Avaliação dos Recursos Tecnológicos na Universidade")
        tec_uni_counts = df['avaliacao_tecnologia_universidade'].value_counts().reset_index()
        tec_uni_counts.columns = ['Avaliação', 'Quantidade']
        # Cria um gráfico de barras horizontais.
        fig_tec_uni = px.bar(tec_uni_counts, y='Avaliação', x='Quantidade', orientation='h',
                             title="Avaliação dos recursos tecnológicos na universidade",
                             text='Quantidade', color_discrete_sequence=[PRIMARY_COLOR])
        st.plotly_chart(fig_tec_uni, use_container_width=True)

    # --- Seção: Frequência de Práticas Leitoras ---
    st.header(" frequência de práticas leitoras")

    # Gráfico da frequência de acesso a diferentes formatos.
    st.subheader("Frequência de Acesso a Livros e Leitura (Pós-Universidade)")
    freq_acesso_counts = df['frequencia_acesso_geral'].value_counts().reindex(ORDER_MAP).fillna(0)
    fig_freq_acesso = px.bar(freq_acesso_counts, x=freq_acesso_counts.index, y=freq_acesso_counts.values,
                             labels={'x': 'Frequência', 'y': 'Quantidade'},
                             title="Frequência geral de acesso ao livro e leitura",
                             text=freq_acesso_counts.values, color_discrete_sequence=[PRIMARY_COLOR])
    fig_freq_acesso.update_traces(textposition='outside')
    st.plotly_chart(fig_freq_acesso, use_container_width=True)

    # Gráfico da frequência de leitura de textos longos.
    st.subheader("Frequência de Leitura de Textos Longos (+20 páginas)")
    freq_longos_counts = df['frequencia_leitura_textos_longos'].value_counts().reindex(ORDER_MAP).fillna(0)
    fig_freq_longos = px.bar(freq_longos_counts, x=freq_longos_counts.index, y=freq_longos_counts.values,
                              labels={'x': 'Frequência', 'y': 'Quantidade'},
                              title="Frequência de leitura de textos longos",
                              color_discrete_sequence=SECONDARY_COLORS) # Usando a nova paleta secundária
    fig_freq_longos.update_traces(textposition='outside')
    st.plotly_chart(fig_freq_longos, use_container_width=True)

    # --- Seção: Respostas Descritivas ---
    st.header("📝 Respostas Descritivas")
    # Expansor para mostrar as justificativas sobre a leitura de textos longos.
    with st.expander("Ver justificativas sobre a leitura de textos longos"):
        # Filtra e exibe as justificativas não nulas.
        justificativas = df['justificativa_leitura_longa'].dropna().tolist()
        for i, just in enumerate(justificativas):
            st.info(f"**Resposta {i+1}:** {just}")

    # Expansor para mostrar as experiências antes e depois da universidade.
    with st.expander("Ver experiências antes e depois da universidade"):
        # Filtra e exibe as experiências não nulas.
        experiencias = df['experiencia_antes_depois'].dropna().tolist()
        for i, exp in enumerate(experiencias):
            st.success(f"**Resposta {i+1}:** {exp}")

    # --- Seção: Raw Data ---
    st.header("📄 Tabela de Dados Brutos")
    # Expansor para mostrar a tabela completa dos dados.
    with st.expander("Clique para ver a tabela de dados completa"):
        st.dataframe(df)