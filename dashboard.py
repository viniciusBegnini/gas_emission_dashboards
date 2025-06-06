import streamlit as st
import pandas as pd
import plotly.express as px

# ---- Page Configs
st.set_page_config(layout= "wide")

# -------------------
#       Funções
# -------------------
def formataNumero(valor):
    if valor >= 1_000_000_000:
        return f'{valor / 1_000_000_000:.2f} b'
    if valor >= 1_000_000:
        return f'{valor / 1_000_000:.2f} m'
    if valor >= 1000:
        return f'{valor / 1000:.2f} k'
    
    return str(valor)


# -------------------
#        Dados
# -------------------
dados = pd.read_csv('emissoes.csv')


# -------------------
#       Tabelas
# -------------------
## Estados
emissoes_estados = dados.groupby('Estado')[['Emissão']].sum().reset_index()
emissoes_estados = dados.drop_duplicates(subset='Estado')[['Estado', 'lat', 'long']].merge(emissoes_estados, on='Estado').reset_index()
emissoes_estados.drop('index', axis=1, inplace=True)

## Setores
emissoes_setores = dados.groupby('Setor de emissão')[['Emissão']].sum().reset_index()

## Anos
emissoes_anos = dados.groupby('Ano')[['Emissão']].sum().sort_values(by='Ano').reset_index()

## Gás
emissoes_gas = dados.groupby('Gás')[['Emissão']].sum().reset_index()

# -------------------
#       Gráficos
# -------------------
## Estados
fig_mapa_emissoes = px.scatter_geo(emissoes_estados,
                                   lat='lat',
                                   lon='long',
                                   scope='south america',
                                   size='Emissão',
                                   hover_name='Estado',
                                   hover_data={'lat': False, 'long': False},
                                   color='Estado',
                                   text='Estado',
                                   title='Total de emissões por estado')

## Setores
fig_emissoes_setores = px.bar(emissoes_setores,
                              x='Emissão', 
                              y='Setor de emissão',
                              color = 'Setor de emissão',
                              text_auto = True,
                              title = 'Total de emissões por setores')
fig_emissoes_setores.update_layout(yaxis_title='', showlegend=False)

## Anos
fig_emissoes_anos = px.line(emissoes_anos,
                            x='Ano',
                            y='Emissão',
                            title= 'Total de emissões por ano')

# -------------------
#      Dashboard
# -------------------
st.title("Emissões de gases de efeito estufa")

tab_home, tab_gas = st.tabs(['Home', 'Gás'])

with tab_home:
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total de emissões", formataNumero(dados['Emissão'].sum()) + ' de toneladas')
        st.plotly_chart(fig_mapa_emissoes)

    with col2:
        idx_maior_emissao = emissoes_anos.index[emissoes_anos['Emissão'] == emissoes_anos['Emissão'].max()]
        ano_mais_poluente = emissoes_anos.iloc[idx_maior_emissao[0]]['Ano'].astype(int)
        emissoes_ano_mais_poluente = emissoes_anos.iloc[idx_maior_emissao[0]]['Emissão']
        st.metric(f'Ano mais poluente: {ano_mais_poluente}', formataNumero(emissoes_ano_mais_poluente) + ' de toneladas')
        st.plotly_chart(fig_emissoes_setores)

    st.plotly_chart(fig_emissoes_anos) 

with tab_gas:
    col1, col2 = st.columns(2)
    with col1:
        idx_gas_maior = emissoes_gas.index[emissoes_gas['Emissão'] == emissoes_gas['Emissão'].max()]
        st.metric('Gás com mais emissões', emissoes_gas.iloc[idx_gas_maior[0]]['Gás'])
    with col2:
        idx_gas_menor = emissoes_gas.index[emissoes_gas['Emissão'] == emissoes_gas['Emissão'].min()]
        st.metric('Gás com mais emissões', emissoes_gas.iloc[idx_gas_menor[0]]['Gás'])

#st.dataframe(emissoes_estados)
