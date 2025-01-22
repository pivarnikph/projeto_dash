import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(page_title="Painel de Emendas Parlamentares 2025", layout="wide")

# Função para formatar valor em Real brasileiro
def formatar_real(valor):
    return f'R$ {valor:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

# Função para calcular percentuais
def calcular_percentuais(df):
    total_geral = df['valor'].sum()
    
    # Percentual por Área
    percentual_area = df.groupby('area')['valor'].sum() / total_geral * 100
    
    # Percentual por Grupo de Despesa
    percentual_grupo_despesa = df.groupby('grupoDespesa')['valor'].sum() / total_geral * 100
    
    return percentual_area, percentual_grupo_despesa

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
        df['transferenciaEspecial'] = df['transferenciaEspecial'].apply(lambda x: 'Finalidade Definida' if x == 'Sim' else 'Finalidade Não Definida')
        df['tipoEmenda'] = df['tipoEmenda'].apply(lambda x: 'Impositiva' if x == True else 'Não Impositiva')
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

# Carregar dados
df = carregar_dados()

# Título da aplicação
st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <img src="https://i.ibb.co/71dBWCx/image-2.png" width="200" alt="Logo">
        <h1>Painel de Emendas Parlamentares 2025</h1>
    </div>
""", unsafe_allow_html=True)

# Sidebar para filtros
st.sidebar.header("Filtros")

# Função para criar dropdown com valores únicos
def criar_dropdown_unico(df, coluna, label):
    valores_unicos = sorted(df[coluna].unique())
    return st.sidebar.selectbox(label, ['Todos'] + list(valores_unicos))

# Criar dropdowns
filtro_deputado = criar_dropdown_unico(df, 'nomeDeputado', "Selecione o Deputado")
filtro_area = criar_dropdown_unico(df, 'area', "Selecione a Área")
filtro_grupo_despesa = criar_dropdown_unico(df, 'grupoDespesa', "Selecione o Grupo de Despesa")

# Aplicar filtros
df_filtrado = df.copy()
if filtro_deputado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['nomeDeputado'] == filtro_deputado]
if filtro_area != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['area'] == filtro_area]
if filtro_grupo_despesa != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['grupoDespesa'] == filtro_grupo_despesa]

# Calcular percentuais
percentual_area, percentual_grupo_despesa = calcular_percentuais(df_filtrado)

# Métricas principais
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total de Emendas", formatar_real(df_filtrado['valor'].sum()))
with col2:
    st.metric("Número de Emendas", df_filtrado.shape[0])
with col3:
    st.metric("Deputados Distintos", df_filtrado['nomeDeputado'].nunique())

# Seção de Análise Percentual
st.header("Análise Percentual de Distribuição")

# Colunas para análise percentual
col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribuição Percentual por Área")
    percentual_area_df = percentual_area.reset_index()
    percentual_area_df.columns = ['Área', 'Percentual']
    percentual_area_df['Percentual'] = percentual_area_df['Percentual'].round(2)
    percentual_area_df = percentual_area_df.sort_values('Percentual', ascending=False)
    st.dataframe(percentual_area_df.style.format({'Percentual': '{:.2f}%'}))

with col2:
    st.subheader("Distribuição Percentual por Grupo de Despesa")
    percentual_grupo_df = percentual_grupo_despesa.reset_index()
    percentual_grupo_df.columns = ['Grupo de Despesa', 'Percentual']
    percentual_grupo_df['Percentual'] = percentual_grupo_df['Percentual'].round(2)
    percentual_grupo_df = percentual_grupo_df.sort_values('Percentual', ascending=False)
    st.dataframe(percentual_grupo_df.style.format({'Percentual': '{:.2f}%'}))

# Gráficos
st.header("Visualizações")
col1, col2 = st.columns(2)

# Gráfico de Valores por Área
with col1:
    st.subheader("Valores por Área")
    # Preparar dados para o gráfico de pizza
    valores_por_area = df_filtrado.groupby('area')['valor'].sum().reset_index()
    
    # Gráfico de pizza interativo com Streamlit
    st.plotly_chart(
        go.Figure(
            data=[go.Pie(
                labels=valores_por_area['area'],
                values=valores_por_area['valor'],
                hole=0.3,
                marker_colors=[f'#{int(0x438E80 - 0x1FB625 * i/len(valores_por_area))}' for i in range(len(valores_por_area))]
            )],
            layout={
                'title': 'Distribuição de Valores por Área',
                'paper_bgcolor': 'rgba(0,0,0,0)',
                'plot_bgcolor': 'rgba(0,0,0,0)'
            }
        ),
        use_container_width=True
    )

# Gráfico de Top 10 Deputados por Quantidade de Emendas
with col2:
    st.subheader("Top 10 Deputados por Quantidade de Emendas")
    # Preparar dados para o gráfico de barras
    top_deputados = df_filtrado.groupby('nomeDeputado')['numero'].count().nlargest(10).reset_index()
    
    # Gráfico de barras interativo com Streamlit
    st.plotly_chart(
        go.Figure(
            data=[go.Bar(
                x=top_deputados['nomeDeputado'],
                y=top_deputados['numero'],
                marker_color=['#438E80', '#41848D', '#3F7A9A', '#3D70A7', '#3B66B4', '#395CC1', '#3752CE', '#3448DB', '#3133E8', '#2F29F5']
            )],
            layout={
                'title': 'Top 10 Deputados por Quantidade de Emendas',
                'xaxis_title': 'Deputado',
                'yaxis_title': 'Quantidade de Emendas',
                'paper_bgcolor': 'rgba(0,0,0,0)',
                'plot_bgcolor': 'rgba(0,0,0,0)'
            }
        ),
        use_container_width=True
    )

# Tabela detalhada
st.header("Detalhamento de Emendas")
tabela_formatada = df_filtrado[['nomeDeputado', 'numero', 'objeto', 'area', 'grupoDespesa', 'valor', 'transferenciaEspecial']].copy()
tabela_formatada['valor'] = tabela_formatada['valor'].apply(formatar_real)

# Renderizar tabela
st.dataframe(tabela_formatada, use_container_width=True)

# Informações relevantes
total_valor = df_filtrado['valor'].sum()
total_emendas = df_filtrado.shape[0]
emendas_finalidade_definida = df_filtrado[df_filtrado['transferenciaEspecial'] == 'Finalidade Definida'].shape[0]
emendas_finalidade_nao_definida = df_filtrado[df_filtrado['transferenciaEspecial'] == 'Finalidade Não Definida'].shape[0]

st.subheader("Informações Relevantes")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.write(f"Total de Valor: {formatar_real(total_valor)}")
with col2:
    st.write(f"Emendas com Finalidade Definida: {emendas_finalidade_definida}")
with col3:
    st.write(f"Emendas com Finalidade Não Definida: {emendas_finalidade_nao_definida}")
with col4:
    st.write(f"Total de Emendas: {total_emendas}")

# Rodapé
st.markdown("---")
st.markdown("**Painel de Emendas Parlamentares 2025 - Subsecretaria Central de Orçamento**")