# --- Bloco Corrigido ---

import pandas as pd
import streamlit as st
import datetime as dt
from st_gsheets_connection import GSheetsConnection # 1. IMPORTAR A CLASSE

# --- Configuração Inicial e Conexão ---

st.set_page_config(page_title="Modelo de Ocorrência")

# Estabelece a conexão com o Google Sheets uma única vez
@st.cache_resource
def get_gsheets_connection():
    # 2. USAR A CLASSE AQUI
    return st.connection("gsheets", type=GSheetsConnection)

conn = get_gsheets_connection()


# --- Carregamento de Dados ---

@st.cache_data
def load_data_from_gsheets(spreadsheet_url):
    """Carrega dados de uma planilha Google, tratando possíveis erros de carregamento."""
    try:
        spreadsheet_id = spreadsheet_url.split("/d/")[1].split("/")[0]
        url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&tqs=0"
        df = pd.read_csv(url)
        return df
    except Exception as e:
        st.error(f"Não foi possível carregar os dados dos equipamentos da planilha: {e}")
        return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro


gsheets_url = "https://docs.google.com/spreadsheets/d/1lUzy2PInVjaL2k7U5R4Wofc-9mvID-EF/edit?usp=sharing&ouid=111800672169498816048&rtpof=true&sd=true"
dados_equipamentos = load_data_from_gsheets(gsheets_url)

# Verifica se as colunas essenciais existem no DataFrame carregado
if not dados_equipamentos.empty:
    required_columns = ['UFV', 'família do equipamento', 'SE', 'equipamento']
    missing_columns = [col for col in required_columns if col not in dados_equipamentos.columns]
    if missing_columns:
        st.error(f'Colunas faltando no arquivo de equipamentos: {", ".join(missing_columns)}')
        st.stop()  # Interrompe a execução se colunas essenciais faltam

# --- Inicialização do Estado da Sessão e Funções de Callback ---

# Bloco único para inicializar todas as chaves do session_state
if 'initialized' not in st.session_state:
    st.session_state['initialized'] = True
    st.session_state['date_ini'] = dt.date.today()
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


def ufv_changed():
    """Callback para resetar seletores dependentes quando a UFV muda."""
    st.session_state['fam_sel'] = None
    st.session_state['se_sel'] = None
    st.session_state['equip_sel'] = None


def fam_changed():
    """Callback para resetar seletores dependentes quando a família do equipamento muda."""
    st.session_state['se_sel'] = None
    st.session_state['equip_sel'] = None


def se_changed():
    """Callback para resetar o seletor de equipamento quando a SE muda."""
    st.session_state['equip_sel'] = None


def clear_form():
    """Limpa todos os campos do formulário, resetando o estado da sessão."""
    st.session_state['date_ini'] = dt.date.today()
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


# --- Layout do Formulário ---

st.header("Formulário de Registro de Ocorrência")

# Seção de Data e Hora
with st.container(border=True):
    col1, col2 = st.columns(2)
    interv_time = dt.timedelta(minutes=1)

    with col1:
        st.date_input('Data inicial da ocorrência:', format='DD/MM/YYYY', key='date_ini')
        st.time_input('Hora inicial:', step=interv_time, key='h_ini')

    with col2:
        st.date_input('Data final da ocorrência:', format='DD/MM/YYYY', key='date_0')
        st.time_input('Hora final:', step=interv_time, key='h_0')

    # Validação das datas e horas
    if st.session_state['date_0'] and st.session_state['h_0'] and st.session_state['date_ini'] and st.session_state[
        'h_ini']:
        data_hora_ini = dt.datetime.combine(st.session_state['date_ini'], st.session_state['h_ini'])
        data_hora_fin = dt.datetime.combine(st.session_state['date_0'], st.session_state['h_0'])
        if data_hora_fin < data_hora_ini:
            st.error("A data e hora final não podem ser anteriores à data e hora inicial.")

# Seção de Seleção de Equipamento com Lógica Corrigida
with st.container(border=True):
    st.subheader("Detalhes do Equipamento")

    # --- Seletor de UFV ---
    ufv_options = [None] + sorted(list(dados_equipamentos['UFV'].unique()))
    ufv_index = ufv_options.index(st.session_state.get('ufv_sel', None))
    st.selectbox('UFV:', ufv_options, index=ufv_index, key='ufv_sel', on_change=ufv_changed,
                 format_func=lambda x: 'Selecione...' if x is None else x)

    # --- Seletor de Família ---
    if st.session_state.get('ufv_sel'):
        fam_options = [None] + sorted(list(
            dados_equipamentos[dados_equipamentos['UFV'] == st.session_state.get('ufv_sel')][
                'família do equipamento'].unique()))
        fam_index = fam_options.index(st.session_state.get('fam_sel', None))
        st.selectbox('Tipo de equipamento:', fam_options, index=fam_index, key='fam_sel', on_change=fam_changed,
                     format_func=lambda x: 'Selecione...' if x is None else x)

    # --- Seletor de SE ---
    if st.session_state.get('fam_sel'):
        se_options = [None] + sorted(list(dados_equipamentos[
                                              (dados_equipamentos['UFV'] == st.session_state.get('ufv_sel')) & (
                                                          dados_equipamentos[
                                                              'família do equipamento'] == st.session_state.get(
                                                      'fam_sel'))]['SE'].unique()))
        se_index = se_options.index(st.session_state.get('se_sel', None))
        st.selectbox('Parte da instalação:', se_options, index=se_index, key='se_sel', on_change=se_changed,
                     format_func=lambda x: 'Selecione...' if x is None else x)

    # --- Seletor de Equipamento ---
    if st.session_state.get('se_sel'):
        equip_options = [None] + sorted(list(dados_equipamentos[
                                                 (dados_equipamentos['UFV'] == st.session_state.get('ufv_sel')) & (
                                                             dados_equipamentos[
                                                                 'família do equipamento'] == st.session_state.get(
                                                         'fam_sel')) & (
                                                             dados_equipamentos['SE'] == st.session_state.get(
                                                         'se_sel'))]['equipamento'].unique()))
        equip_index = equip_options.index(st.session_state.get('equip_sel', None))
        st.selectbox('Equipamento:', equip_options, index=equip_index, key='equip_sel',
                     format_func=lambda x: 'Selecione...' if x is None else x)

# Seção de Descrição da Ocorrência
with st.container(border=True):
    st.subheader("Descrição da Ocorrência")
    st.text_area('Descrição inicial:', key='descr_ini_ocr')
    st.multiselect('Proteções atuantes:',
                   ['21 - Prot. Distância', '27 - Subtensão', '59 - Sobretensão', '50 - Sobrecorrente Inst.',
                    '51 - Sobrecorrente Temp.', '50/62BF - Falha de abertura DJ', '87T - Diferencial do TR',
                    '87B - Diferencial de Barras', '81U/O - Sub/Sobrefrequência', 'Nenhuma atuação de proteção'],
                   key='prot_up')
    st.checkbox('Atuação de Bloqueio?', key='bloq_chk')
    st.text_area('Observações:', key='obs_ocr')

# --- Botões de Ação ---

col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    # --- SUBSTITUA O BLOCO DO BOTÃO 'Gravar' POR ESTE ---

    with col_btn1:
        if st.button('Gravar Ocorrência', type="primary", use_container_width=True):
            # Validação para garantir que os campos obrigatórios foram preenchidos
            if not all([st.session_state.get(k) for k in
                        ['date_ini', 'h_ini', 'ufv_sel', 'fam_sel', 'se_sel', 'equip_sel']]):
                st.warning("Por favor, preencha todos os campos de data, hora e equipamento antes de gravar.")
            else:
                data_ini_formatada = st.session_state.date_ini.strftime('%d/%m/%Y')
                hora_ini_formatada = st.session_state.h_ini.strftime('%H:%M')
                data_fin_formatada = st.session_state.date_0.strftime('%d/%m/%Y') if st.session_state.date_0 else '-'
                hora_fin_formatada = st.session_state.h_0.strftime('%H:%M') if st.session_state.h_0 else '-'

                ocorrencia_data = pd.DataFrame([{
                    "Data de Início": data_ini_formatada,
                    "Hora de Início": hora_ini_formatada,
                    "Data de Término": data_fin_formatada,
                    "Hora de Término": hora_fin_formatada,
                    "UFV": st.session_state.ufv_sel,
                    "Família do Equipamento": st.session_state.fam_sel,
                    "SE": st.session_state.se_sel,
                    "Equipamento": st.session_state.equip_sel,
                    "Descrição da Ocorrência": st.session_state.descr_ini_ocr,
                    "Proteções Atuantes": ", ".join(st.session_state.prot_up),
                    "Atuação de Bloqueio": "Sim" if st.session_state.bloq_chk else "Não",
                    "Observações": st.session_state.obs_ocr
                }])

                try:
                    # CORREÇÃO: Usando .add_rows para uma operação segura de acréscimo
                    conn.add_rows(worksheet="Ocorrências", data=ocorrencia_data)

                    st.success("Ocorrência gravada com sucesso!")

                    # Gera o resumo para o usuário copiar
                    txt_ocr = (
                        f"- Data/hora de início: {data_ini_formatada} - {hora_ini_formatada}\n"
                        f"- Data/hora de término: {data_fin_formatada} - {hora_fin_formatada}\n"
                        f"- Equipamento: {st.session_state.se_sel} - {st.session_state.equip_sel}\n"
                        f"- Proteção atuada: {', '.join(st.session_state.prot_up) or 'Nenhuma'}\n"
                        f'- Bloqueio: {"Sim" if st.session_state.bloq_chk else "Não"}\n'
                        f"- Descrição: {st.session_state.descr_ini_ocr}\n"
                        f"- Observações: {st.session_state.obs_ocr}"
                    )
                    st.text_area("Resumo da Ocorrência (para copiar):", value=txt_ocr, height=250)

                    # Limpa o formulário após o sucesso
                    clear_form()
                    st.rerun()  # Força a atualização da página para limpar campos e recarregar a lista

                except Exception as e:
                    st.error(f"Ocorreu um erro ao gravar a ocorrência: {e}")

            try:
                # Atualiza a planilha usando o nome da aba correto
                aba_existente = conn.read(worksheet="Ocorrências", usecols=list(range(12)))
                df_atualizado = pd.concat([aba_existente, ocorrencia_data], ignore_index=True)
                conn.update(worksheet="Ocorrências", data=df_atualizado)

                st.success("Ocorrência gravada com sucesso!")

                # Gera o resumo para o usuário copiar
                txt_ocr = (
                    f"- Data/hora de início: {data_ini_formatada} - {hora_ini_formatada}\n"
                    f"- Data/hora de término: {data_fin_formatada} - {hora_fin_formatada}\n"
                    f"- Equipamento: {st.session_state.se_sel} - {st.session_state.equip_sel}\n"
                    f"- Proteção atuada: {', '.join(st.session_state.prot_up) or 'Nenhuma'}\n"
                    f'- Bloqueio: {"Sim" if st.session_state.bloq_chk else "Não"}\n'
                    f"- Descrição: {st.session_state.descr_ini_ocr}\n"
                    f"- Observações: {st.session_state.obs_ocr}"
                )
                st.text_area("Resumo da Ocorrência (para copiar):", value=txt_ocr, height=250)

                # Limpa o formulário após o sucesso
                clear_form()

            except Exception as e:
                st.error(f"Ocorreu um erro ao gravar a ocorrência: {e}")

with col_btn2:
    if st.button('Limpar Campos', on_click=clear_form, use_container_width=True):
        st.toast("Formulário limpo!")

# --- Seção para Exibir Dados Registrados ---

with st.expander("Ver Ocorrências Registradas"):
    try:
        ocorrencias_df = conn.read(worksheet="Ocorrências", usecols=list(range(12)), ttl="10m")
        if not ocorrencias_df.empty:
            st.dataframe(ocorrencias_df.sort_index(ascending=False))
        else:
            st.info("Nenhuma ocorrência registrada ainda.")
    except Exception as e:
        st.error(f"Não foi possível ler as ocorrências da planilha: {e}")