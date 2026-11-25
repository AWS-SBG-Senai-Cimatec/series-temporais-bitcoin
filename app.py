from __future__ import annotations

from pathlib import Path
import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

# ==============================================================================
# CONFIGURAÇÃO CENTRAL DOS ARQUIVOS DE PREVISÕES
# Prioriza previsoes_modelos.csv em data/ e faz fallback para exemplo.
# ==============================================================================
CAMINHOS_PREVISOES = [
    Path("data/previsoes_modelos.csv"),
    Path("para_o_grupo/previsoes_modelos.csv"),
    Path("para_o_grupo/previsoes_exemplo.csv"),
    Path("data/previsoes_exemplo.csv"),
    Path("previsoes_exemplo.csv"),
]

MAPA_ROTULOS = {
    "real": "Real",
    "naive": "Naive (base)",
    "regressao_linear": "Regressão Linear",
    "ridge": "Ridge",
    "knn": "KNN (variação)",
    "exemplo": "Exemplo",
}

st.set_page_config(
    page_title="Bitcoin ML | Comparador de Séries Temporais",
    page_icon="📈",
    layout="wide",
)

st.markdown(
    """
    <style>
        .stApp {
            background-color: #f1f5f9;
        }
        section[data-testid="stSidebar"] {
            background-color: #e2e8f0;
            border-right: 1px solid #cbd5e1;
        }
        .hero-box {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #f8fafc;
            border-radius: 14px;
            padding: 22px 26px;
            margin-bottom: 14px;
            border: 1px solid #334155;
        }
        .hero-box h1 {
            color: #ffffff !important;
            font-size: 1.72rem !important;
            margin: 0 0 6px 0 !important;
            padding: 0 !important;
        }
        .hero-box p {
            color: #cbd5e1;
            margin: 0;
            font-size: 0.98rem;
        }
        .card-guia {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 14px;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        }
        .card-guia h3 {
            margin: 0 0 8px 0;
            font-size: 1.05rem;
            color: #0f172a;
        }
        .card-guia p {
            margin: 0 0 8px 0;
            color: #334155;
            font-size: 0.94rem;
            line-height: 1.5;
        }
        .card-guia ul {
            margin: 4px 0 10px 0;
            padding-left: 18px;
            color: #334155;
            font-size: 0.92rem;
            line-height: 1.55;
        }
        .glossario-box {
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 12px 16px;
            margin-top: 8px;
            font-size: 0.91rem;
            color: #1e293b;
            line-height: 1.55;
        }
        .destaque-box {
            background-color: #ffffff;
            border: 1px solid #cbd5e1;
            border-left: 5px solid #2563eb;
            border-radius: 12px;
            padding: 15px 18px;
            margin: 12px 0 16px 0;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        }
        .destaque-box p {
            margin: 0;
            color: #0f172a;
            font-size: 0.96rem;
            line-height: 1.55;
        }
        div[data-testid="stMetric"] {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 14px 16px;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        }
        div[data-testid="stMetricLabel"] > div {
            color: #475569;
            font-weight: 500;
        }
        div[data-testid="stMetricValue"] {
            color: #0f172a;
            font-weight: 700;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def resolver_caminho_csv(caminhos: list[Path]) -> Path:
    """Resolve o primeiro arquivo de previsões disponível na lista."""
    for candidato in caminhos:
        if candidato.exists():
            return candidato
    return caminhos[0]


def formatar_nome_curto(nome: str) -> str:
    """Deixa os rótulos curtos e claros para legenda e tabelas."""
    baixa = nome.strip().lower()
    if baixa in MAPA_ROTULOS:
        return MAPA_ROTULOS[baixa]
    return nome.replace("_", " ").title()


def montar_grafico_linhas(
    df_series: pd.DataFrame,
    nome_data: str,
    titulo_eixo_y: str,
) -> alt.Chart:
    """Gráfico de linhas temporal com paleta fixa."""
    df_long = df_series.reset_index().rename(
        columns={df_series.index.name or "index": nome_data}
    )
    df_melt = df_long.melt(
        id_vars=[nome_data],
        var_name="Série",
        value_name="Valor",
    ).dropna(subset=["Valor"])

    series_unicas = list(dict.fromkeys(df_melt["Série"].tolist()))
    cores_base = ["#2563eb", "#dc2626", "#16a34a", "#d97706", "#7c3aed", "#0891b2"]
    escala_cores = [cores_base[i % len(cores_base)] for i in range(len(series_unicas))]

    color_enc = alt.Color(
        "Série:N",
        scale=alt.Scale(domain=series_unicas, range=escala_cores),
        legend=alt.Legend(
            title=None,
            orient="bottom",
            columns=min(len(series_unicas), 4),
        ),
    )

    return (
        alt.Chart(df_melt)
        .mark_line(strokeWidth=2.2, interpolate="linear")
        .encode(
            x=alt.X(f"{nome_data}:T", title="Data"),
            y=alt.Y("Valor:Q", title=titulo_eixo_y, scale=alt.Scale(zero=False)),
            color=color_enc,
            tooltip=[
                alt.Tooltip(f"{nome_data}:T", title="Data", format="%d/%m/%Y"),
                alt.Tooltip("Série:N", title="Série"),
                alt.Tooltip("Valor:Q", title="Valor", format=",.2f"),
            ],
        )
        .properties(height=390)
        .interactive()
    )


def montar_grafico_barras_erro(df_comparativo: pd.DataFrame) -> alt.Chart:
    """Gráfico de barras com rótulos de erro médio (%) sobre cada barra."""
    df_bar = df_comparativo.copy()
    df_bar["Rotulo_Pct"] = df_bar["Erro médio (%)"].map(
        lambda v: f"{v:.2f}%" if pd.notna(v) else "-"
    )

    cores_base = ["#2563eb", "#dc2626", "#16a34a", "#d97706", "#7c3aed", "#0891b2"]
    modelos = df_bar["Série"].tolist()
    escala_cores = [cores_base[i % len(cores_base)] for i in range(len(modelos))]

    max_val = (
        float(df_bar["Erro médio (%)"].max())
        if df_bar["Erro médio (%)"].notna().any()
        else 1.0
    )
    limite_superior = max(max_val * 1.25, 0.5)

    base = alt.Chart(df_bar).encode(
        x=alt.X(
            "Série:N",
            sort="-y",
            title="Série avaliada (quanto menor a barra, menor o erro)",
            axis=alt.Axis(labelAngle=0),
        ),
        y=alt.Y(
            "Erro médio (%):Q",
            title="Erro médio frente ao Real (%)",
            scale=alt.Scale(domain=[0, limite_superior]),
        ),
    )

    barras = base.mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6, size=48).encode(
        color=alt.Color(
            "Série:N",
            scale=alt.Scale(domain=modelos, range=escala_cores),
            legend=None,
        ),
        tooltip=[
            alt.Tooltip("Série:N", title="Série"),
            alt.Tooltip("Erro médio (%):Q", title="Erro médio (%)", format=".2f"),
            alt.Tooltip(
                "Diferença média (pontos):Q",
                title="Diferença média (pontos)",
                format=",.2f",
            ),
            alt.Tooltip(
                "Dias até 1% do real:Q",
                title="Dias até 1% do real (%)",
                format=".1f",
            ),
        ],
    )

    rotulos = base.mark_text(
        dy=-10,
        fontSize=13,
        fontWeight="bold",
        color="#0f172a",
    ).encode(
        text="Rotulo_Pct:N",
    )

    return (barras + rotulos).properties(height=315)


@st.cache_data
def carregar_dados_previsao(
    caminho: Path,
) -> tuple[pd.DataFrame, str, str | None, list[str]]:
    """Carrega e padroniza o CSV de previsões."""
    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado em '{caminho}'. "
            "Gere data/previsoes_modelos.csv ou mantenha para_o_grupo/previsoes_exemplo.csv."
        )

    df = pd.read_csv(caminho)
    if df.empty:
        raise ValueError("O arquivo CSV existe, mas está vazio.")

    df.columns = [str(col).strip() for col in df.columns]

    candidatos_data = [
        col
        for col in df.columns
        if any(
            chave in col.lower()
            for chave in ["data", "date", "ds", "timestamp", "dia"]
        )
    ]
    col_data = candidatos_data[0] if candidatos_data else df.columns[0]

    df[col_data] = pd.to_datetime(df[col_data], errors="coerce")
    df = df.dropna(subset=[col_data]).sort_values(col_data)

    if df.empty:
        raise ValueError(
            f"Não foi possível converter datas válidas na coluna '{col_data}'."
        )

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
        col
        for col in df.columns
        if any(
            chave in col.lower()
            for chave in [
                "real",
                "actual",
                "true",
                "y_true",
                "close",
                "preco",
                "preço",
            ]
        )
    ]
    coluna_real = candidatos_real[0] if candidatos_real else None
    colunas_previsao = [col for col in df.columns if col != coluna_real]

    return df, col_data, coluna_real, colunas_previsao


def calcular_metricas_serie(
    df: pd.DataFrame,
    coluna_real: str,
    coluna_prev: str,
) -> dict[str, float] | None:
    """Calcula diferença média em pontos, erro percentual médio e % de dias até 1% do real."""
    par = df[[coluna_real, coluna_prev]].dropna()
    if par.empty:
        return None

    diff_abs = (par[coluna_real] - par[coluna_prev]).abs()
    mae = float(diff_abs.mean())
    denominador = par[coluna_real].replace(0, np.nan)
    erro_pct = (diff_abs / denominador).abs() * 100
    mape = float(erro_pct.mean()) if erro_pct.notna().any() else float("nan")
    ate_1pct = (
        float((erro_pct.dropna() <= 1.0).mean() * 100)
        if erro_pct.notna().any()
        else float("nan")
    )

    return {
        "mae": mae,
        "mape": mape,
        "ate_1pct": ate_1pct,
    }


def gerar_tabela_comparativa(
    df: pd.DataFrame,
    coluna_real: str,
    colunas_prev: list[str],
) -> pd.DataFrame:
    """Monta tabela comparativa ordenada do menor para o maior erro médio (%)."""
    linhas = []
    for col_p in colunas_prev:
        res = calcular_metricas_serie(df, coluna_real, col_p)
        if res:
            linhas.append(
                {
                    "Série": formatar_nome_curto(col_p),
                    "col_original": col_p,
                    "Erro médio (%)": (
                        round(res["mape"], 2) if np.isfinite(res["mape"]) else None
                    ),
                    "Diferença média (pontos)": round(res["mae"], 2),
                    "Dias até 1% do real": (
                        round(res["ate_1pct"], 1)
                        if np.isfinite(res["ate_1pct"])
                        else None
                    ),
                }
            )
    if not linhas:
        return pd.DataFrame()

    df_comp = pd.DataFrame(linhas).sort_values(
        by="Erro médio (%)",
        ascending=True,
        na_position="last",
    )
    return df_comp.reset_index(drop=True)


def montar_tabela_extremos(
    df: pd.DataFrame,
    col_real: str,
    col_prev: str,
    maiores: bool = True,
) -> pd.DataFrame:
    """Retorna os 5 dias com maior ou menor diferença absoluta frente ao valor real."""
    nome_prev = formatar_nome_curto(col_prev)
    base = pd.DataFrame(
        {
            "Data": df.index.strftime("%d/%m/%Y"),
            "Real": df[col_real].values,
            nome_prev: df[col_prev].values,
            "Diferença": (df[col_real] - df[col_prev]).abs().values,
        }
    ).dropna(subset=["Diferença"])

    base["Erro %"] = (base["Diferença"] / base["Real"].replace(0, np.nan)).abs() * 100
    ordenado = base.sort_values("Diferença", ascending=not maiores).head(5).copy()

    ordenado["Real"] = ordenado["Real"].map(lambda v: f"{v:,.2f}")
    ordenado[nome_prev] = ordenado[nome_prev].map(lambda v: f"{v:,.2f}")
    ordenado["Diferença"] = ordenado["Diferença"].map(lambda v: f"{v:,.2f}")
    ordenado["Erro %"] = ordenado["Erro %"].map(
        lambda v: f"{v:.2f}%" if pd.notna(v) else "-"
    )

    return ordenado.reset_index(drop=True)


# ==============================================================================
# CABEÇALHO E GUIA AUTOEXPLICATIVO
# ==============================================================================
st.markdown(
    """
    <div class="hero-box">
        <h1>📈 Comparador de Técnicas de Machine Learning — Séries Temporais (Bitcoin)</h1>
        <p>Veja de forma simples como previsões de séries temporais se comparam ao valor real e à referência base.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

caminho_ativo = resolver_caminho_csv(CAMINHOS_PREVISOES)

try:
    df_base, nome_col_data, col_real, cols_prev = carregar_dados_previsao(
        caminho_ativo
    )
except Exception as erro:
    st.error(f"Não foi possível carregar os dados de previsão: {erro}")
    st.info(
        "Dica: gere `data/previsoes_modelos.csv` no notebook `04a_lineares_e_knn.ipynb` "
        "ou verifique se `para_o_grupo/previsoes_exemplo.csv` existe."
    )
    st.stop()

usando_exemplo = "exemplo" in caminho_ativo.name.lower()
status_badge = (
    f"🧪 Modo demonstração — base exemplo (`{caminho_ativo}`)"
    if usando_exemplo
    else f"✅ Base de modelos gerada (`{caminho_ativo}`)"
)
st.caption(f"{status_badge}  |  Eixo de tempo: `{nome_col_data}`")

st.markdown(
    """
    <div class="card-guia">
        <h3>🧭 O que é este projeto e como usar o painel sozinho</h3>
        <p>
            Este aplicativo compara técnicas de previsão em <strong>séries temporais</strong> no histórico do
            <strong>Bitcoin</strong> contra o valor <strong>Real</strong> e contra uma regra de referência simples
            (<strong>Naive</strong>). Tudo é atualizado automaticamente quando você muda o período ou as séries no menu lateral.
        </p>
        <ul>
            <li><strong>Cartões de resumo:</strong> mostram quem teve menor erro médio (%) no período escolhido, em qual % dos dias a previsão ficou a até 1% do valor real e qual foi o último valor real registrado.</li>
            <li><strong>Aba "Curvas no Tempo":</strong> mostra como os valores evoluem dia a dia — quanto mais próxima a curva de previsão estiver da curva <strong>Real</strong>, melhor.</li>
            <li><strong>Aba "Ranking e Maiores Erros":</strong> coloca os modelos em ordem do menor para o maior erro médio (%) e exibe os 5 dias com maior e menor diferença.</li>
            <li><strong>Aba "Tabela e Download":</strong> mostra os valores exatos do período selecionado e permite baixar o arquivo em CSV.</li>
        </ul>
        <div class="glossario-box">
            <strong>Glossário rápido para qualquer pessoa entender:</strong><br>
- <strong>Real:</strong> o valor histórico observado de fato no dia (é o gabarito).<br>
- <strong>Naive (base):</strong> uma referência simples (como repetir o valor anterior) usada para testar se um modelo entrega algo além do óbvio.<br>
- <strong>Exemplo:</strong> dado ilustrativo de teste usado quando a base gerada em <code>data/previsoes_modelos.csv</code> ainda não está presente na máquina.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==============================================================================
# BARRA LATERAL (FILTROS)
# ==============================================================================
st.sidebar.header("🎛️ Filtros")
st.sidebar.caption("Escolha o período e quais linhas mostrar nos gráficos.")

data_min = df_base.index.min().date()
data_max = df_base.index.max().date()

atalho_periodo = st.sidebar.radio(
    "Período rápido",
    options=["Período completo", "Últimos 30 dias", "Últimos 90 dias", "Personalizado"],
    index=0,
)

if atalho_periodo == "Últimos 30 dias":
    inicio_padrao = max(
        data_min, (pd.Timestamp(data_max) - pd.Timedelta(days=30)).date()
    )
    fim_padrao = data_max
elif atalho_periodo == "Últimos 90 dias":
    inicio_padrao = max(
        data_min, (pd.Timestamp(data_max) - pd.Timedelta(days=90)).date()
    )
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
padrao_series = ([col_real] if col_real else []) + cols_prev[:4]
if not padrao_series:
    padrao_series = todas_series

series_selecionadas = st.sidebar.multiselect(
    "Séries selecionadas",
    options=todas_series,
    default=padrao_series,
    format_func=formatar_nome_curto,
)

# ==============================================================================
# RESUMO EXECUTIVO E CARTÕES DE RESULTADOS
# ==============================================================================
periodo_txt = f"{data_ini.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"

df_comp = (
    gerar_tabela_comparativa(df_filtrado, col_real, cols_prev)
    if col_real and col_real in df_filtrado.columns and cols_prev
    else pd.DataFrame()
)

if not df_comp.empty:
    melhor = df_comp.iloc[0]
    melhor_nome = str(melhor["Série"])
    melhor_erro_pct = melhor["Erro médio (%)"]
    melhor_diff_pts = melhor["Diferença média (pontos)"]
    melhor_ate_1pct = melhor["Dias até 1% do real"]

    st.markdown(
        f"""
        <div class="destaque-box">
            <p>
                <strong>O que os números dizem entre {periodo_txt}:</strong> a série com menor erro médio foi
                <strong>{melhor_nome}</strong>, com erro percentual médio de <strong>{melhor_erro_pct:.2f}%</strong>
                (diferença média de <strong>{melhor_diff_pts:,.2f}</strong> pontos) e ficando a até 1% do
                valor real em <strong>{melhor_ate_1pct:.1f}%</strong> dos dias analisados.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        "Menor erro no período",
        melhor_nome,
        help="Série que teve o menor erro percentual médio neste período.",
    )
    c2.metric(
        "Erro médio (%)",
        f"{melhor_erro_pct:.2f}%" if pd.notna(melhor_erro_pct) else "-",
        help="Média do erro percentual em relação ao valor real. Quanto menor, mais perto do real a série ficou.",
    )
    c3.metric(
        "Dias até 1% do real",
        f"{melhor_ate_1pct:.1f}%" if pd.notna(melhor_ate_1pct) else "-",
        help="Em qual porcentagem dos dias a diferença ficou em até 1% do valor real.",
    )
    ultimo_real_txt = (
        f"{float(df_filtrado[col_real].dropna().iloc[-1]):,.2f}"
        if col_real and df_filtrado[col_real].notna().any()
        else "-"
    )
    c4.metric(
        "Último valor (Real)",
        ultimo_real_txt,
        help="Último valor real registrado no período selecionado.",
    )
else:
    c1, c2, c3 = st.columns(3)
    c1.metric("Registros no período", f"{len(df_filtrado):,}".replace(",", "."))
    c2.metric("Data inicial", data_ini.strftime("%d/%m/%Y"))
    c3.metric("Data final", data_fim.strftime("%d/%m/%Y"))

# ==============================================================================
# ABAS DE APRESENTAÇÃO DOS RESULTADOS (CURVAS PRIMEIRO, DEPOIS RANKING)
# ==============================================================================
if not series_selecionadas:
    st.info("Selecione pelo menos uma série na barra lateral para visualizar os resultados.")
    st.stop()

aba_curvas, aba_ranking, aba_tabela = st.tabs(
    [
        "📈 Curvas no Tempo",
        "🏆 Ranking e Maiores Erros",
        "📋 Tabela e Download",
    ]
)

with aba_curvas:
    st.subheader("Séries temporais no período selecionado")
    st.caption(
        "Como ler: cada linha mostra a evolução diária de uma série. Quando as linhas andam coladas umas às outras, "
        "a previsão está próxima do valor real. Para ver detalhes de perto, escolha 'Últimos 30 dias' ou 'Últimos 90 dias' no menu lateral."
    )
    df_plot = df_filtrado[series_selecionadas].rename(columns=formatar_nome_curto)
    chart_curvas = montar_grafico_linhas(
        df_series=df_plot,
        nome_data=nome_col_data,
        titulo_eixo_y="Valor",
    )
    st.altair_chart(chart_curvas, use_container_width=True)

with aba_ranking:
    if not df_comp.empty:
        melhor_serie_txt = str(df_comp.iloc[0]["Série"])
        melhor_pct_txt = (
            f"{df_comp.iloc[0]['Erro médio (%)']:.2f}%"
            if pd.notna(df_comp.iloc[0]["Erro médio (%)"])
            else "-"
        )
        st.info(
            f"**Como ler este ranking:** barras menores significam erro menor (melhor proximidade do valor real). "
            f"Neste recorte, **{melhor_serie_txt}** ficou em 1º lugar com **{melhor_pct_txt}** de erro médio."
        )

        col_esq, col_dir = st.columns([1.15, 1])

        with col_esq:
            st.subheader("Erro médio (%) por série")
            st.caption(
                "Cada barra mostra o erro médio percentual frente ao valor real (quanto menor, melhor)."
            )
            st.altair_chart(montar_grafico_barras_erro(df_comp), use_container_width=True)

        with col_dir:
            st.subheader("Comparativo geral no período")
            st.caption(
                "Tabela ordenada do menor para o maior erro médio (%). "
                "'Dias até 1% do real' indica em quantos dias o desvio não passou de 1%."
            )
            st.dataframe(
                df_comp.drop(columns=["col_original"]),
                use_container_width=True,
                hide_index=True,
            )

        modelos_nao_naive = [c for c in cols_prev if "naive" not in c.lower()]
        serie_analise = modelos_nao_naive[0] if modelos_nao_naive else cols_prev[0]
        nome_serie_analise = formatar_nome_curto(serie_analise)

        st.divider()
        st.subheader(f"Dias com maior e menor diferença — {nome_serie_analise}")
        st.caption(
            "À esquerda, os 5 dias em que a previsão mais se afastou do valor real; "
            "à direita, os 5 dias em que a previsão ficou mais próxima do valor real."
        )

        col_maior, col_menor = st.columns(2)

        with col_maior:
            st.markdown("**Top 5 dias com maior diferença (maiores desvios)**")
            st.dataframe(
                montar_tabela_extremos(df_filtrado, col_real, serie_analise, maiores=True),
                use_container_width=True,
                hide_index=True,
            )

        with col_menor:
            st.markdown("**Top 5 dias com menor diferença (mais próximos do real)**")
            st.dataframe(
                montar_tabela_extremos(df_filtrado, col_real, serie_analise, maiores=False),
                use_container_width=True,
                hide_index=True,
            )
    else:
        st.info(
            "Assim que o CSV contiver uma coluna de valor real e colunas de previsão, "
            "o ranking entre séries e os dias de maior/menor diferença aparecerão aqui."
        )

with aba_tabela:
    st.subheader("Dados detalhados do recorte")
    st.caption(
        "Confira os valores dia a dia do período escolhido ou clique no botão abaixo para
