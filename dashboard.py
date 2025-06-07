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
#       Sidebar
# -------------------

st.sidebar.title('Filtros')

with st.sidebar.expander('Ano'):
    ano_min = dados['Ano'].min()
    ano_max = dados['Ano'].max()
    todos_anos = st.checkbox('Todos os anos', value=True)

    if todos_anos:
       f_anos = (ano_min, ano_max) 
    else:    
        f_anos = st.slider("Selecione o ano", ano_min, ano_max, (ano_min, ano_max))

with st.sidebar.expander('Setor de emissão'):
    setores = dados['Setor de emissão'].unique()
    f_setores = st.multiselect('Selecione os setores', setores, default=setores)

with st.sidebar.expander('Gás'):
    gases = dados['Gás'].unique()
    f_gases = st.multiselect('Selecione os gáses', gases, default=gases)

with st.sidebar.expander('Estados ou regiôes'):
    filtro_regiao = st.checkbox('Filtrar por região?')
    estados = dados['Estado'].unique()

    if filtro_regiao:
        regioes = ['Brasil', 'Sudeste', 'Sul']
        regiao = st.selectbox('Selecione a região', regioes)    

        if regiao == 'Brasil':
            f_estados = dados['Estado'].unique()
        elif regiao == 'Sudeste':
            f_estados = ['MG', 'SP', 'RJ', 'ES']
        elif regiao == 'Sul':
            f_estados = ['RS', 'SC', 'PR']
    else:
        f_estados = st.multiselect('Selecione os estados', estados, default=estados)
        

## Filtro  dos dados
query = '''
@f_anos[0] <= Ano <= @f_anos[1] and \
`Setor de emissão` in @f_setores and \
`Gás` in @f_gases and \
Estado in @f_estados
'''

dados = dados.query(query)

# -------------------
#       Tabelas
# -------------------
## Estados
emissoes_estados = dados.groupby('Estado')[['Emissão']].sum().reset_index()
emissoes_estados = dados.drop_duplicates(subset='Estado')[['Estado', 'lat', 'long']].merge(emissoes_estados, on='Estado').reset_index()
emissoes_estados.drop('index', axis=1, inplace=True)

emissoes_estado_gas = dados.groupby(['Estado', 'Gás'])[['Emissão']].sum().reset_index()
emissoes_estado_gas = emissoes_estado_gas.loc[emissoes_estado_gas.groupby('Estado')['Emissão'].idxmax()]

emissoes_estado_setor = dados.groupby(['Estado', 'Setor de emissão'])[['Emissão']].sum().reset_index()
emissoes_estado_setor = emissoes_estado_setor.loc[emissoes_estado_setor.groupby('Estado')['Emissão'].idxmax()].sort_values(by='Emissão', ascending=False)

## Setores
emissoes_setores = dados.groupby('Setor de emissão')[['Emissão']].sum().reset_index()

## Anos
emissoes_anos = dados.groupby('Ano')[['Emissão']].sum().sort_values(by='Ano').reset_index()

## Gás
emissoes_gas = dados.groupby('Gás')[['Emissão']].sum().reset_index()
emissoes_gas['Percentual'] = ((emissoes_gas['Emissão'] / emissoes_gas['Emissão'].sum()) * 100).apply(lambda x : f'{x:2f}').astype(float)

emissoes_gas_ano = dados.groupby(['Ano', 'Gás'])[['Emissão']].mean().reset_index()
emissoes_gas_ano = emissoes_gas_ano.pivot_table(index='Ano', columns='Gás', values='Emissão')

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

fig_emissoes_estados = px.bar(emissoes_estados,
                              x='Estado',
                              y='Emissão',
                              text_auto=True,
                              color='Estado',
                              title='Total de emissões por estado')

fig_emissoes_estado_gas = px.sunburst(emissoes_estado_gas,
                                      path=['Estado', 'Gás'],
                                      values='Emissão',
                                      color='Gás',
                                      title='Gás mais emitido por estado')

fig_emissoes_estado_setor = px.bar(emissoes_estado_setor,
                                   y='Emissão',
                                   x='Estado',
                                   color='Setor de emissão',
                                   text_auto=True,
                                   title='Setor com mais emissões por estado')

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

## Gás
fig_perc_emissoes_gas = px.pie(emissoes_gas,
                               names='Gás',
                               values='Emissão',
                               title='Percentual de emissões de gás')

fig_emissoes_gas = px.bar(emissoes_gas,
                          x='Emissão',
                          y='Gás',
                          text_auto=True,
                          color='Gás',
                          title='Total de emissões por gás')
fig_emissoes_gas.update_layout(yaxis_title='', showlegend=False)

# -------------------
#      Dashboard
# -------------------
st.title("Emissões de gases de efeito estufa")

tab_home, tab_gas, tab_estado = st.tabs(['Home', 'Gás', 'Estado'])

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

    st.plotly_chart(fig_perc_emissoes_gas)
    st.plotly_chart(fig_emissoes_gas)

    with st.container(height=500):
        st.subheader('Média das emissões dos gases por ano')
        for gas in emissoes_gas_ano.columns:
            fig = px.line(emissoes_gas_ano[gas], title=gas)
            fig.update_layout(yaxis_title='Emissão', showlegend=False)
            st.plotly_chart(fig)


with tab_estado:
    col1, col2 = st.columns(2, border=True)
    with col1:
        idx_maior_emissao = emissoes_estados.index[emissoes_estados['Emissão'] == emissoes_estados['Emissão'].max()]
        st.metric('Estado com mais emissões', emissoes_estados.iloc[idx_maior_emissao[0]]['Estado'])

    with col2:
        idx_menor_emissao = emissoes_estados.index[emissoes_estados['Emissão'] == emissoes_estados['Emissão'].min()]
        st.metric('Estado com menos emissões', emissoes_estados.iloc[idx_menor_emissao[0]]['Estado'])
        
    st.plotly_chart(fig_emissoes_estados)

    col1, col2 = st.columns(2, border=True)
    with col1:
        st.plotly_chart(fig_emissoes_estado_gas)
    
    with col2:
        st.plotly_chart(fig_emissoes_estado_setor)
