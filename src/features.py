"""Carga e preparação das séries diárias de Bitcoin para modelagem."""

from pathlib import Path

import numpy as np
import pandas as pd


COLUNAS_PRECO = ("open", "high", "low", "close", "volume")


def _interpretar_datas(valores: pd.Series, nome: str = "data") -> pd.Series:
    """Interpreta datas ISO, dia/mês/ano, mês/dia/ano e Unix s/ms em UTC.

    Datas numéricas são consideradas epoch quando têm magnitude compatível;
    datas textuais ambíguas como 03/04/2024 seguem a convenção brasileira
    (dia/mês/ano). Strings ISO como 2024-03-04 não são ambíguas.
    """
    numericos = pd.to_numeric(valores, errors="coerce")
    nao_vazios = valores.notna() & valores.astype(str).str.strip().ne("")
    if nao_vazios.any() and numericos[nao_vazios].notna().all():
        digitos = valores.astype(str).str.strip().str.fullmatch(r"\d{8}")
        if digitos[nao_vazios].all():
            return pd.to_datetime(valores.astype("string"), format="%Y%m%d", utc=True, errors="coerce")
        escala = "ms" if numericos[nao_vazios].abs().median() > 1e11 else "s"
        return pd.to_datetime(numericos, unit=escala, utc=True, errors="coerce")

    textos = valores.astype("string").str.strip()
    try:
        return pd.to_datetime(textos, format="mixed", dayfirst=True, utc=True, errors="coerce")
    except (TypeError, ValueError):  # pandas anterior ao suporte de format="mixed"
        return pd.to_datetime(textos, dayfirst=True, utc=True, errors="coerce")


def carregar_diario(caminho: str | Path) -> pd.DataFrame:
    """Carrega o CSV diário, valida colunas e devolve índice temporal crescente.

    O arquivo deve conter uma coluna ``data`` (ou datas no índice) e as colunas
    OHLCV. Datas são interpretadas em UTC e normalizadas para o início do dia.
    """
    caminho = Path(caminho)
    if not caminho.is_file():
        raise FileNotFoundError(f"Arquivo de dados não encontrado: {caminho}")

    df = pd.read_csv(caminho)
    if "data" in df.columns:
        datas = _interpretar_datas(df.pop("data"))
    elif "Unnamed: 0" in df.columns:
        datas = _interpretar_datas(df.pop("Unnamed: 0"))
    else:
        raise ValueError("O CSV precisa ter uma coluna 'data'.")

    ausentes = sorted(set(COLUNAS_PRECO) - set(df.columns))
    if ausentes:
        raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(ausentes)}")
    if datas.isna().any():
        raise ValueError("Há datas inválidas na coluna 'data'.")

    df.index = datas.dt.floor("D").dt.tz_localize(None)
    df.index.name = "data"
    df = df.loc[:, COLUNAS_PRECO].apply(pd.to_numeric, errors="coerce")
    if df.isna().any().any():
        raise ValueError("Há valores ausentes ou não numéricos nas colunas OHLCV.")
    if not np.isfinite(df.to_numpy(dtype=float)).all():
        raise ValueError("Há valores infinitos nas colunas OHLCV.")
    if df.index.has_duplicates:
        raise ValueError("Há mais de uma linha para a mesma data diária.")
    return df.sort_index()


def criar_features(diario: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Cria lags conhecidos no dia *t* para prever o fechamento do dia t+1.

    O índice da saída representa a data em que a previsão seria feita. O alvo
    fica alinhado com essa data e contém o ``close`` do dia seguinte.
    """
    ausentes = sorted({"close", "volume"} - set(diario.columns))
    if ausentes:
        raise ValueError(f"Colunas necessárias ausentes: {', '.join(ausentes)}")
    if not isinstance(diario.index, pd.DatetimeIndex):
        raise TypeError("O índice do DataFrame deve ser um DatetimeIndex.")
    base = diario.sort_index()
    if base.index.has_duplicates:
        raise ValueError("O índice não pode conter datas duplicadas.")
    if base.empty:
        raise ValueError("O DataFrame diário está vazio.")
    dias_esperados = pd.date_range(base.index.min(), base.index.max(), freq="D")
    if not base.index.equals(dias_esperados):
        raise ValueError("A série tem lacunas ou datas fora da frequência diária; corrija os dados antes de criar o alvo do dia seguinte.")
    features = pd.DataFrame(index=base.index)
    features["close_lag_1"] = base["close"]
    features["close_lag_7"] = base["close"].shift(7)
    features["close_lag_30"] = base["close"].shift(30)
    features["volume_lag_1"] = base["volume"] if "volume" in base else float("nan")
    features["retorno_1d"] = base["close"].pct_change(fill_method=None)
    alvo = base["close"].shift(-1).rename("close_dia_seguinte")
    conjunto = features.join(alvo).dropna()
    return conjunto[features.columns], conjunto["close_dia_seguinte"]


def dividir_treino_teste(
    df: pd.DataFrame, fim_treino: str | pd.Timestamp
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Divide cronologicamente; ``fim_treino`` é inclusivo e nada é embaralhado."""
    if not isinstance(df.index, pd.DatetimeIndex):
        raise TypeError("O índice do DataFrame deve ser um DatetimeIndex.")
    limite_utc = pd.to_datetime(str(fim_treino), dayfirst=True, utc=True, errors="coerce")
    if pd.isna(limite_utc):
        raise ValueError(f"Data fim_treino inválida: {fim_treino!r}")
    limite = limite_utc.tz_localize(None)
    # Corte por dia: formatos com horário não devem excluir parte do dia final.
    limite = limite.normalize()
    ordenado = df.sort_index()
    if ordenado.empty:
        raise ValueError("O DataFrame para divisão está vazio.")
    treino = ordenado.loc[ordenado.index <= limite]
    teste = ordenado.loc[ordenado.index > limite]
    if treino.empty or teste.empty:
        raise ValueError("A data fim_treino deve deixar treino e teste não vazios.")
    return treino, teste
