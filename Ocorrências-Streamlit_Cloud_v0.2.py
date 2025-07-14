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

gsheets_url = "https://docs.google.com/spreadsheets/d/1lUzy2PInVjaL2k7U5R4Wofc-9mvID-EF/edit?usp=sharing&ouid=111800672169498816048&rtpof=true&sd=true" # Substitua pela sua URL
dados = load_data_from_gsheets(gsheets_url)

required_columns = ['UFV','família do equipamento','SE','equipamento']
missing_columns = [col for col in required_columns if col not in dados.columns]

# Inicialização do st.session_state (manter como está)
if 'date_ini' not in st.session_state:
    st.session_state['date_ini'] = dt.datetime.today()
if 'h_ini' not in st.session_state:
    st.session_state['h_ini'] = None
if 'date_0' not in st.session_state:
    st.session_state['date_0'] = None
if 'h_0' not in st.session_state:
    st.session_state['h_0'] = None
if 'ufv_sel' not in st.session_state:
    st.session_state['ufv_sel'] = None
if 'fam_sel' not in st.session_state:
    st.session_state['fam_sel'] = None
if 'se_sel' not in st.session_state:
    st.session_state['se_sel'] = None
if 'equip_sel' not in st.session_state:
    st.session_state['equip_sel'] = None
if 'descr_ini_ocr' not in st.session_state:
    st.session_state['descr_ini_ocr'] = ''
if 'prot_up' not in st.session_state:
    st.session_state['prot_up'] = []
if 'bloq_chk' not in st.session_state:
    st.session_state['bloq_chk'] = False
if 'obs_ocr' not in st.session_state:
    st.session_state['obs_ocr'] = ''

def clear_form():
    st.session_state['date_ini'] = dt.datetime.today()
    st.session_state['h_ini'] = None
    st.session_state['date_0'] = None
    st.session_state['h_0'] = None
    st.session_state['ufv_sel'] = None
    st.session_state['fam_sel'] = None
    st.session_state['se_sel'] = None
    st.session_state['equip_sel'] = None
    st.session_state['descr_ini_ocr'] = ''
    st.session_state['prot_up'] = []
    st.session_state['bloq_chk'] = False
    st.session_state['obs_ocr'] = ''

col1, col2 = st.columns(2, gap='large', vertical_alignment='center', border=1)

interv_time = dt.timedelta(minutes=1)

with col1:
    date_ini = st.date_input('Data inicial da ocorrência:', format='DD/MM/YYYY', key='date_ini', value=st.session_state['date_ini'])
    h_ini = st.time_input('Hora inicial:', value=st.session_state['h_ini'], step=interv_time, key='h_ini')

with col2:
    date_0 = st.date_input('Data final da ocorrência:', format='DD/MM/YYYY', value=st.session_state['date_0'], key='date_0')
    h_0 = st.time_input('Hora final:', value=st.session_state['h_0'], step=interv_time, key='h_0')

    if date_0 is None:
        date_fin = '-'
    else:
        date_fin = date_0

    if h_0 is None:
        h_fin = '-'
    else:
        h_fin = h_0

# Validação das datas e horas (manter como está)
if st.session_state['date_0'] and st.session_state['h_0'] and st.session_state['date_ini'] and st.session_state['h_ini']:
    data_hora_ini = dt.datetime.combine(st.session_state['date_ini'], st.session_state['h_ini'])
    data_hora_fin = dt.datetime.combine(st.session_state['date_0'], st.session_state['h_0'])
    if data_hora_fin < data_hora_ini:
        st.error("A data e hora final da ocorrência não podem ser anteriores à data e hora inicial.")

# Seleção de Equipamento (manter como está)
if missing_columns:
    st.error(f'Colunas faltando no arquivo Excel: {", ".join(missing_columns)}')
else:
    ufv_0 = dados['UFV'].unique()
    ufv_sel = st.selectbox('Selecione a UFV: ', ufv_0, index=None, key='ufv_sel', index=ufv_0.tolist().index(st.session_state['ufv_sel']) if st.session_state['ufv_sel'] in ufv_0 else None)

    fam_sel = None
    if st.session_state['ufv_sel']:
        fam_0 = dados[dados['UFV'] == st.session_state['ufv_sel']]['família do equipamento'].unique()
        fam_sel = st.selectbox('Selecione o tipo de equipamento: ', fam_0, index=None, key='fam_sel', index=fam_0.tolist().index(st.session_state['fam_sel']) if st.session_state['fam_sel'] in fam_0 else None)

    se_sel = None
    if st.session_state['fam_sel']:
        se_0 = dados[(dados['UFV'] == st.session_state['ufv_sel']) & (dados['família do equipamento'] == st.session_state['fam_sel'])]['SE'].unique()
        se_sel = st.selectbox('Selecione parte da instalação: ', se_0, index=None, key='se_sel', index=se_0.tolist().index(st.session_state['se_sel']) if st.session_state['se_sel'] in se_0 else None)

    equip_sel = None
    if st.session_state['se_sel']:
        equip_0 = dados[(dados['UFV'] == st.session_state['ufv_sel']) &
                        (dados['família do equipamento'] == st.session_state['fam_sel']) &
                        (dados['SE'] == st.session_state['se_sel'])]['equipamento'].unique()
        equip_sel = st.selectbox('Selecione o Equipamento: ', equip_0, index=None, key='equip_sel', index=equip_0.tolist().index(st.session_state['equip_sel']) if st.session_state['equip_sel'] in equip_0 else None)

    descr_ini_ocr = st.text_area('Descrição inicial da Ocorrência:', key='descr_ini_ocr', value=st.session_state['descr_ini_ocr'])

    prot_up = st.multiselect('Proteções atuantes?',
                             ['21 - Prot. Distância','27 - Subtensão','59 - Sobretensão','50 - Sobrecorrente Inst.',
                              '51 - Sobrecorrente Temp.','50/62BF - Falha de abertura DJ','87T - Diferencial do TR',
                              '87B - Diferencial de Barras','81U/O - Sub/Sobrefrequência','Nenhuma atuação de proteção'],
                             key='prot_up', default=st.session_state['prot_up'])

    bloq_chk = st.checkbox('Atuação de Bloqueio?', key='bloq_chk', value=st.session_state['bloq_chk'])

    obs_ocr = st.text_area('Observações:', key='obs_ocr', value=st.session_state['obs_ocr'])

    if st.button('Gravar'):
        data_ini_formatada = st.session_state['date_ini'].strftime('%d/%m/%Y')
        data_fin_formatada = date_fin if date_fin == '-' else date_fin.strftime('%d/%m/%Y')

        # Conectando ao Google Sheets usando st.connection
        conn = st.connection("gsheets", type=st.gsheets_connection.GSheetsConnection)

        # Criando um DataFrame com os dados da ocorrência
        ocorrencia_data = pd.DataFrame([{
            "Data de Início": data_ini_formatada,
            "Hora de Início": st.session_state['h_ini'].strftime('%H:%M') if st.session_state['h_ini'] else '',
            "Data de Término": data_fin_formatada,
            "Hora de Término": st.session_state['h_0'].strftime('%H:%M') if st.session_state['h_0'] else '',
            "UFV": st.session_state['ufv_sel'],
            "Família do Equipamento": st.session_state['fam_sel'],
            "SE": st.session_state['se_sel'],
            "Equipamento": st.session_state['equip_sel'],
            "Descrição da Ocorrência": st.session_state['descr_ini_ocr'],
            "Proteções Atuantes": ", ".join(st.session_state['prot_up']),
            "Atuação de Bloqueio": "Sim" if st.session_state['bloq_chk'] else "Não",
            "Observações": st.session_state['obs_ocr']
        }])

        # Nome da aba onde você quer salvar os dados (crie essa aba se não existir)
        nome_aba_ocorrencias = "Ocorrências"

        try:
            # Usando a conexão para adicionar os dados à planilha
            conn.add_rows(sheet_name=nome_aba_ocorrencias, data=ocorrencia_data)
            st.success("Ocorrência gravada com sucesso na planilha!")
            clear_form() # Limpa o formulário após a gravação
        except Exception as e:
            st.error(f"Ocorreu um erro ao gravar a ocorrência: {e}")

        txt_ocr = ( # Manter a exibição do resumo
            f"'- Data/hora de início: {data_ini_formatada} - {st.session_state['h_ini']}.\n"
            f'- Data/hora de término: {data_fin_formatada} - {h_fin}.\n'
            f'- Equipamento: {st.session_state['se_sel']} - {st.session_state['equip_sel']}. - Proteção atuada: {st.session_state['prot_up']} - Bloqueio: {"Sim" if st.session_state['bloq_chk'] else "Não"}\n'
            f'- Descrição da Ocorrência: {st.session_state['descr_ini_ocr']}\n'
            f'- Observações: {st.session_state['obs_ocr']}'
        )
        st.text_area("Resumo da Ocorrência:", value=txt_ocr, height=200)

if st.button('Limpar', on_click=clear_form):
    st.warning("Campos limpos!")