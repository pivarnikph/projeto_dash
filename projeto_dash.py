import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(page_title="Painel de Emendas Parlamentares 2025", layout="wide")

# Função para carregar dados
@st.cache_data
def carregar_dados():
    try:
        df = pd.read_excel('Testev1. IA Emendas 2025.xlsx')
        
        # Mapeamento de colunas
        df = df.rename(columns={
            'AUTOR': 'nomeDeputado',
            'NÚMERO': 'numero',
            'OBJETO': 'objeto',
            'ÁREA': 'area',
            'LOCALIZAÇÃO': 'localizacao',
            'GND': 'grupoDespesa',
            'BENEFICIÁRIO': 'beneficiario',
            'VALOR': 'valor',
            'TRANSFERÊNCIA ESPECIAL': 'transferenciaEspecial',
            'VALI': 'tipoEmenda'
        })
        
        # Tratamento de dados
        df['objeto'] = df['objeto'].fillna('Não especificado')
        df['area'] = df['area'].fillna('Não definida')
        df['localizacao'] = df['localizacao'].fillna('Não definida')
        df['grupoDespesa'] = df['grupoDespesa'].apply(lambda x: f'GND {x}' if pd.notna(x) else 'Não definido')
        df['beneficiario'] = df['beneficiario'].fillna('Não definido')
        df['valor'] = df['valor'].fillna(0)
        df['transferenciaEspecial'] = df['transferenciaEspecial'].apply(lambda x: 'Transferência Especial' if x == 'Sim' else 'Outro Tipo')
        df['tipoEmenda'] = df['tipoEmenda'].apply(lambda x: 'Impositiva' if x == True else 'Não Impositiva')
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

# Carregar dados
df = carregar_dados()

# Título da aplicação
st.title("Painel de Emendas Parlamentares 2025")

# Sidebar para filtros
st.sidebar.header("Filtros")
filtro_deputado = st.sidebar.text_input("Filtrar por Deputado")
filtro_area = st.sidebar.text_input("Filtrar por Área")
filtro_grupo_despesa = st.sidebar.text_input("Filtrar por Grupo de Despesa")

# Aplicar filtros
df_filtrado = df.copy()
if filtro_deputado:
    df_filtrado = df_filtrado[df_filtrado['nomeDeputado'].str.contains(filtro_deputado, case=False)]
if filtro_area:
    df_filtrado = df_filtrado[df_filtrado['area'].str.contains(filtro_area, case=False)]
if filtro_grupo_despesa:
    df_filtrado = df_filtrado[df_filtrado['grupoDespesa'].str.contains(filtro_grupo_despesa, case=False)]

# Métricas principais
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total de Emendas", f"R$ {df_filtrado['valor'].sum():,.2f}")
with col2:
    st.metric("Número de Emendas", df_filtrado.shape[0])
with col3:
    st.metric("Deputados Distintos", df_filtrado['nomeDeputado'].nunique())

# Gráficos
st.header("Visualizações")
col1, col2 = st.columns(2)

# Gráfico de Valores por Área
with col1:
    st.subheader("Valores por Área")
    valores_por_area = df_filtrado.groupby('area')['valor'].sum().reset_index()
    fig_area = px.pie(valores_por_area, values='valor', names='area', 
                      title='Distribuição de Valores por Área')
    st.plotly_chart(fig_area, use_container_width=True)

# Gráfico de Top 10 Deputados por Valor de Emenda
with col2:
    st.subheader("Top 10 Deputados por Valor de Emenda")
    top_deputados = df_filtrado.groupby('nomeDeputado')['valor'].sum().nlargest(10).reset_index()
    fig_deputados = px.bar(top_deputados, x='nomeDeputado', y='valor', 
                           title='Top 10 Deputados por Valor de Emenda')
    st.plotly_chart(fig_deputados, use_container_width=True)

# Tabela detalhada
st.header("Detalhamento de Emendas")
st.dataframe(df_filtrado[['nomeDeputado', 'numero', 'area', 'grupoDespesa', 'valor']]
              .style.format({'valor': 'R$ {:.2f}'}))

# Rodapé
st.markdown("---")
st.markdown("**Painel de Emendas Parlamentares 2025 - Análise Interativa**")