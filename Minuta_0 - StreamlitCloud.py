import pandas as pd
import streamlit as st
import datetime as dt

st.set_page_config(page_title="Modelo de Ocorrência")

@st.cache_data
def load_data_from_gsheets(spreadsheet_url):
    spreadsheet_id = spreadsheet_url.split("/d/")[1].split("/")[0]
    url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&tqs=0"
    df = pd.read_csv(url)
    return df

# Substitua a URL da sua planilha publicada aqui
gsheets_url = "https://docs.google.com/spreadsheets/d/1lUzy2PInVjaL2k7U5R4Wofc-9mvID-EF/edit?usp=sharing&ouid=111800672169498816048&rtpof=true&sd=true"
dados = load_data_from_gsheets(gsheets_url)

# Colunas do DataFrame
required_columns = ['UFV','família do equipamento','SE','equipamento']
missing_columns = [col for col in required_columns if col not in dados.columns]

col1, col2 = st.columns(2, gap='large', vertical_alignment='center', border=1)

interv_time = dt.timedelta(minutes=1)

with col1:
    date_ini = st.date_input('Data inicial da ocorrência:', format='DD/MM/YYYY', value=dt.datetime.today())
    h_ini = st.time_input('Hora inicial:', value=None, step=interv_time)

with col2:
    date_0 = st.date_input('Data final da ocorrência:', format='DD/MM/YYYY', value=None)

    if date_0 is None:
        date_fin = '-'
    else:
        date_fin = date_0

    h_0 = st.time_input('Hora final:', value=None, step=interv_time)

    if h_0 is None:
        h_fin = '-'
    else:
        h_fin = h_0

# Seleção de Equipamento
if missing_columns:
    st.error(f'Colunas faltando no arquivo Excel: {", ".join(missing_columns)}')

else:
    ufv_0 = dados['UFV'].unique()
    ufv_sel = st.selectbox('Selecione a UFV: ', ufv_0, index=None)

    fam_0 = dados[dados['UFV'] == ufv_sel]['família do equipamento'].unique()
    fam_sel = st.selectbox('Selecione o tipo de equipamento: ', fam_0, index=None)

    se_0 = dados[(dados['UFV'] == ufv_sel) & (dados['família do equipamento'] == fam_sel)]['SE'].unique()
    se_sel = st.selectbox('Selecione parte da instalação: ', se_0, index=None)

    equip_0 = dados[(dados['UFV'] == ufv_sel) &
                    (dados['família do equipamento'] == fam_sel) &
                    (dados['SE'] == se_sel)]['equipamento'].unique()
    equip_sel = st.selectbox('Selecione o Equipamento: ', equip_0, index=None)

descr_ini_ocr = st.text_area('Descrição inicial da Ocorrência:')

prot_up = st.multiselect('Proteções atuantes?',
                         ['21 - Prot. Distância','27 - Subtensão','59 - Sobretensão','50 - Sobrecorrente Inst.',
                          '51 - Sobrecorrente Temp.','50/62BF - Falha de abertura DJ','87T - Diferencial do TR',
                          '87B - Diferencial de Barras','81U/O - Sub/Sobrefrequência','Nenhuma atuação de proteção'])

bloq_chk = st.checkbox('Atuação de Bloqueio?')
if bloq_chk is True:
    bloq_chk = 'Sim'
else:
    bloq_chk = 'Não'

obs_ocr = st.text_area('Observações:')

if st.button('Gravar'):
    txt_ocr = (
        f"'- Data/hora de início: {date_ini} - {h_ini}.\n"
        f'- Data/hora de término: {date_fin} - {h_fin}.\n'
        f'- Equipamento: {se_sel} - {equip_sel}. - Proteção atuada: {prot_up} - Bloqueio: {bloq_chk}\n'
        f'- Descrição da Ocorrência: {descr_ini_ocr}\n'
        f'- Observações: {obs_ocr}'
    )
    st.text_area("Resumo da Ocorrência:", value=txt_ocr, height=200)

if st.button('Limpar'):
    st.warning("Campos limpos!")
    st.rerun()

