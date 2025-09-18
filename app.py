import streamlit as st
import pandas as pd
from streamlit_elements import elements, mui, html

# -------------------------
# Funções auxiliares
# -------------------------
def extrair_percentual(valor):
    if pd.isna(valor):
        return 0.0
    if isinstance(valor, str):
        valor = valor.replace('%','').replace(',','.')
        try:
            return float(valor)
        except:
            return 0.0
    elif isinstance(valor, (float, int)):
        return float(valor)*100 if valor < 1 else float(valor)
    return 0.0

def extrair_percentual_imovel(valor):
    if pd.isna(valor):
        return 0.0
    if isinstance(valor, str):
        valor = valor.replace('%','').replace(',','.')
        try:
            return float(valor)
        except:
            return 0.0
    elif isinstance(valor, (float, int)):
        return float(valor)*100 if valor <= 1 else float(valor)
    return 0.0

# -------------------------
# Paths das planilhas
# -------------------------
path_porcentagem = r"\\172.17.67.14\Ares Motos\controladoria\Contabilidade\Contabilidade_Societaria\PORCENTAGEM_DE_PARTICIPACAO_NAS_EMPRESAS_2025.xlsx"
path_patrimonios = r"\\172.17.67.14\Ares Motos\controladoria\Contabilidade\Escrituras_e_Matriculas\2025_Controle_Patrimonial_Fernando_Linhares_SEMESTRE_2_2025.xlsx"

# -------------------------
# Carregar planilhas
# -------------------------
try:
    df_participacao = pd.read_excel(path_porcentagem, sheet_name=0)
    df_patrimonio = pd.read_excel(path_patrimonios, sheet_name=0)
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    st.stop()

# -------------------------
# Transformar matriz Dono x Empresa em formato longo
# -------------------------
df_long = df_participacao.melt(id_vars=['Controladas'], var_name='Dono', value_name='% Participação')
df_long = df_long[df_long['% Participação'].notna() & (df_long['% Participação'] != 0)]
df_long['Dono'] = df_long['Dono'].str.replace(r'\s*% de Participação\s*', '', regex=True)
df_long['% Participação'] = df_long['% Participação'].apply(extrair_percentual)

# -------------------------
# Layout principal
# -------------------------
st.set_page_config(page_title="Mapa Patrimonial", layout="wide")
st.title("🌐 Mapa Patrimonial: Dono → Empresa → Imóveis")

st.sidebar.header("Filtros")
filtro_dono = st.sidebar.multiselect(
    "Selecione Proprietários",
    options=sorted(df_long['Dono'].unique()),
    default=sorted(df_long['Dono'].unique())
)

df_filtrado = df_long[df_long['Dono'].isin(filtro_dono)]

# -------------------------
# Interface com streamlit-elements
# -------------------------
with elements("layout"):
    # Um grid responsivo para os cartões de cada proprietário
    with mui.Grid(container=True, spacing=2):
        for dono in df_filtrado['Dono'].unique():
            empresas_dono = df_filtrado[df_filtrado['Dono'] == dono]

            with mui.Grid(item=True, xs=12, md=6, lg=4):
                with mui.Card(elevation=4, style={"padding":"1rem","background":"#FFF3CD"}):
                    mui.Typography(f"👤 {dono}", variant="h6", gutterBottom=True)

                    # Empresas em acordeão
                    for _, row in empresas_dono.iterrows():
                        empresa = row['Controladas']
                        perc_emp = row['% Participação']

                        with mui.Accordion():
                            with mui.AccordionSummary(expandIcon="⬇️"):
                                mui.Typography(f"🏢 {empresa}  ({perc_emp:.2f}%)")
                            with mui.AccordionDetails():
                                imoveis = df_patrimonio[df_patrimonio['EMPRESA'] == empresa]
                                if imoveis.empty:
                                    mui.Typography("Sem imóveis vinculados", color="text.secondary")
                                else:
                                    for _, imovel in imoveis.iterrows():
                                        perc_imov = extrair_percentual_imovel(imovel['% PART NO IMOVEL'])
                                        with mui.Card(variant="outlined",
                                                      style={"marginBottom":"0.5rem","padding":"0.5rem","background":"#E8F5E9"}):
                                            mui.Typography(f"🏠 {imovel['NOME DO IMÓVEL']}", variant="subtitle1")
                                            mui.Typography(f"Percentual na empresa: {perc_imov:.2f}%", color="text.secondary")
                                            mui.Typography(f"{imovel['ENDEREÇO COMPLETO']}", color="text.secondary", style={"fontSize":"0.85rem"})
