from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st

# ==============================================================================
# CONFIGURAÇÃO CENTRAL DO ARQUIVO DE PREVISÕES
# Troque este caminho quando o Lucca gerar o CSV oficial dos modelos/testes.
# ==============================================================================
CAMINHO_PREVISOES = Path("para_o_grupo/previsoes_exemplo.csv")
CAMINHOS_FALLBACK = [
    Path("data/previsoes_exemplo.csv"),
    Path("previsoes_exemplo.csv"),
]

st.set_page_config(
    page_title="Bitcoin ML | Comparador de Séries Temporais",
    page_icon="📈",
    layout="wide",
)


def resolver_caminho_csv(caminho_principal: Path, fallbacks: list[Path]) -> Path:
    """Resolve o caminho do CSV priorizando o caminho principal configurado."""
    if caminho_principal.exists():
        return caminho_principal
    for candidato in fallbacks:
        if candidato.exists():
            return candidato
    return caminho_principal


@st.cache_data
def carregar_dados_previsao(caminho: Path) -> tuple[pd.DataFrame, str, str | None, list[str]]:
    """
    Carrega e padroniza o CSV de previsões.
    Retorna: (dataframe_indexado_por_data, nome_coluna_data, coluna_real, colunas_previsao)
    """
    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado em '{caminho}'. "
            "Verifique o caminho em CAMINHO_PREVISOES no topo do app.py."
        )

    df = pd.read_csv(caminho)
    if df.empty:
        raise ValueError("O arquivo CSV existe, mas está vazio.")

    df.columns = [str(col).strip() for col in df.columns]

    candidatos_data = [
        col for col in df.columns
        if any(chave in col.lower() for chave in ["data", "date", "ds", "timestamp", "dia"])
    ]
    col_data = candidatos_data[0] if candidatos_data else df.columns[0]

    df[col_data] = pd.to_datetime(df[col_data], errors="coerce")
    df = df.dropna(subset=[col_data]).sort_values(col_data)

    if df.empty:
        raise ValueError(f"Não foi possível converter datas válidas na coluna '{col_data}'.")

    df = df[~df[col_data].duplicated(keep="last")].set_index(col_data)

    colunas_numericas: list[str] = []
    for col in df.columns:
        convertida = pd.to_numeric(df[col], errors="coerce")
        if convertida.notna().sum() > 0:
            df[col] = convertida
            colunas_numericas.append(col)

    if not colunas_numericas:
        raise ValueError("Nenhuma coluna numérica válida encontrada para plotagem.")

    df = df[colunas_numericas]

    candidatos_real = [
        col for col in df.columns
        if any(chave in col.lower() for chave in ["real", "actual", "true", "y_true", "close", "preco", "preço"])
    ]
    coluna_real = candidatos_real[0] if candidatos_real else None
    colunas_previsao = [col for col in df.columns if col != coluna_real]

    return df, col_data, coluna_real, colunas_previsao


def calcular_metricas_rapidas(
    df: pd.DataFrame,
    coluna_real: str | None,
    colunas_selecionadas: list[str],
) -> dict[str, str]:
    """Calcula métricas resumidas simples para o recorte filtrado."""
    resumo: dict[str, str] = {
        "registros": f"{len(df):,}".replace(",", "."),
    }

    if coluna_real and coluna_real in df.columns and df[coluna_real].notna().any():
        ultimo_real = df[coluna_real].dropna().iloc[-1]
        resumo["ultimo_real"] = f"{ultimo_real:,.2f}"

        previsoes_ativas = [c for c in colunas_selecionadas if c != coluna_real]
        if previsoes_ativas:
            modelos_nao_naive = [c for c in previsoes_ativas if "naive" not in c.lower()]
            alvo_prev = modelos_nao_naive[0] if modelos_nao_naive else previsoes_ativas[0]

            par = df[[coluna_real, alvo_prev]].dropna()
            if not par.empty:
                erro_abs = (par[coluna_real] - par[alvo_prev]).abs()
                mae = erro_abs.mean()
                resumo["mae_ref"] = f"{mae:,.2f}"
                resumo["serie_ref"] = alvo_prev

                denominador = par[coluna_real].replace(0, np.nan)
                mape = ((erro_abs / denominador).abs().mean()) * 100
                if np.isfinite(mape):
                    resumo["mape_ref"] = f"{mape:.2f}%"

    return resumo


st.title("📈 Comparador de Técnicas de ML — Séries Temporais (Bitcoin)")
st.markdown(
    "Visualização interativa para acompanhar **valores reais vs. previsões** e comparar "
    "modelos ao longo do tempo."
)

caminho_ativo = resolver_caminho_csv(CAMINHO_PREVISOES, CAMINHOS_FALLBACK)

try:
    df_base, nome_col_data, col_real, cols_prev = carregar_dados_previsao(caminho_ativo)
except Exception as erro:
    st.error(f"Não foi possível carregar os dados de previsão: {erro}")
    st.info(
        "Dica: confira se o arquivo CSV existe no caminho configurado em "
        "`CAMINHO_PREVISOES` no topo do `app.py`."
    )
    st.stop()

usando_exemplo = "exemplo" in caminho_ativo.name.lower()
status_badge = (
    f"🧪 Modo de teste com arquivo de exemplo: `{caminho_ativo}`"
    if usando_exemplo
    else f"✅ Fonte de dados ativa: `{caminho_ativo}`"
)
st.caption(f"{status_badge}  |  Coluna de data detectada: `{nome_col_data}`")

st.sidebar.header("🎛️ Filtros e Visualização")

data_min = df_base.index.min().date()
data_max = df_base.index.max().date()

atalho_periodo = st.sidebar.radio(
    "Janela rápida",
    options=["Período completo", "Últimos 30 dias", "Últimos 90 dias", "Personalizado"],
    index=0,
)

if atalho_periodo == "Últimos 30 dias":
    inicio_padrao = max(data_min, (pd.Timestamp(data_max) - pd.Timedelta(days=30)).date())
    fim_padrao = data_max
elif atalho_periodo == "Últimos 90 dias":
    inicio_padrao = max(data_min, (pd.Timestamp(data_max) - pd.Timedelta(days=90)).date())
    fim_padrao = data_max
else:
    inicio_padrao, fim_padrao = data_min, data_max

selecao_datas = st.sidebar.date_input(
    "Intervalo de datas",
    value=(inicio_padrao, fim_padrao),
    min_value=data_min,
    max_value=data_max,
)

if isinstance(selecao_datas, tuple) and len(selecao_datas) == 2:
    data_ini, data_fim = pd.Timestamp(selecao_datas[0]), pd.Timestamp(selecao_datas[1])
elif isinstance(selecao_datas, tuple) and len(selecao_datas) == 1:
    data_ini = data_fim = pd.Timestamp(selecao_datas[0])
else:
    data_ini = data_fim = pd.Timestamp(selecao_datas)

if data_ini > data_fim:
    st.sidebar.error("A data inicial não pode ser maior que a data final.")
    st.stop()

df_filtrado = df_base.loc[data_ini:data_fim]

if df_filtrado.empty:
    st.warning("Nenhum dado encontrado no intervalo de datas selecionado.")
    st.stop()

todas_series = list(df_filtrado.columns)
padrao_series = ([col_real] if col_real else []) + cols_prev[:3]
if not padrao_series:
    padrao_series = todas_series

series_selecionadas = st.sidebar.multiselect(
    "Séries para exibir no gráfico",
    options=todas_series,
    default=padrao_series,
)

tipo_grafico = st.sidebar.selectbox(
    "Tipo de visualização",
    options=["Linha (Real vs. Previsto)", "Área"],
    index=0,
)

metricas = calcular_metricas_rapidas(df_filtrado, col_real, series_selecionadas)

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("Observações no período", metricas["registros"])

if "ultimo_real" in metricas:
    col_m2.metric(f"Último valor ({col_real})", metricas["ultimo_real"])
else:
    col_m2.metric("Séries disponíveis", str(len(todas_series)))

if "mae_ref" in metricas:
    col_m3.metric(f"MAE ({metricas['serie_ref']})", metricas["mae_ref"])
else:
    col_m3.metric("Data inicial", data_ini.strftime("%d/%m/%Y"))

if "mape_ref" in metricas:
    col_m4.metric(f"MAPE ({metricas['serie_ref']})", metricas["mape_ref"])
else:
    col_m4.metric("Data final", data_fim.strftime("%d/%m/%Y"))

st.divider()

if not series_selecionadas:
    st.info("Selecione pelo menos uma série na barra lateral para renderizar o gráfico.")
    st.stop()

aba_grafico, aba_erros, aba_tabela = st.tabs(
    ["📊 Real vs. Previsto", "📉 Diferença / Erro Absoluto", "📋 Dados e Exportação"]
)

with aba_grafico:
    st.subheader("Comparação temporal: Real vs. Previsto")
    df_plot = df_filtrado[series_selecionadas]
    if tipo_grafico == "Área":
        st.area_chart(df_plot, use_container_width=True)
    else:
        st.line_chart(df_plot, use_container_width=True)

with aba_erros:
    st.subheader("Diferença absoluta entre valor real e previsões")
    if col_real and col_real in df_filtrado.columns:
        modelos_no_filtro = [c for c in df_filtrado.columns if c != col_real]
        if modelos_no_filtro:
            df_erros = pd.DataFrame(index=df_filtrado.index)
            for modelo in modelos_no_filtro:
                df_erros[f"Erro abs. ({modelo})"] = (
                    df_filtrado[col_real] - df_filtrado[modelo]
                ).abs()
            st.line_chart(df_erros, use_container_width=True)
        else:
            st.info("Nenhuma coluna de previsão encontrada além da coluna real.")
    else:
        st.info(
            "Nenhuma coluna de valor real foi identificada automaticamente no CSV "
            "(ex.: `real`, `y_true`, `close`). Assim que o CSV tiver a coluna real "
            "e as previsões, o erro absoluto aparece aqui automaticamente."
        )

with aba_tabela:
    st.subheader("Tabela de registros filtrados")
    df_exibicao = df_filtrado[series_selecionadas].copy()
    df_exibicao.index = df_exibicao.index.strftime("%Y-%m-%d")
    df_exibicao.index.name = nome_col_data

    st.dataframe(df_exibicao, use_container_width=True)

    csv_exportacao = df_exibicao.to_csv(index=True).encode("utf-8")
    st.download_button(
        label="⬇️ Baixar recorte filtrado (CSV)",
        data=csv_exportacao,
        file_name="previsoes_filtradas.csv",
        mime="text/csv",
    )