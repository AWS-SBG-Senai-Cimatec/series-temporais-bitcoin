"""Carga e preparação das séries diárias de Bitcoin para modelagem."""

from pathlib import Path

import pandas as pd


COLUNAS_PRECO = ("open", "high", "low", "close", "volume")


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
        datas = pd.to_datetime(df.pop("data"), utc=True, errors="coerce")
    elif "Unnamed: 0" in df.columns:
        datas = pd.to_datetime(df.pop("Unnamed: 0"), utc=True, errors="coerce")
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
    if df.index.has_duplicates:
        raise ValueError("Há mais de uma linha para a mesma data diária.")
    return df.sort_index()


def criar_features(diario: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Cria lags conhecidos no dia *t* para prever o fechamento do dia t+1.

    O índice da saída representa a data em que a previsão seria feita. O alvo
    fica alinhado com essa data e contém o ``close`` do dia seguinte.
    """
    if "close" not in diario.columns:
        raise ValueError("O DataFrame precisa conter a coluna 'close'.")
    if not isinstance(diario.index, pd.DatetimeIndex):
        raise TypeError("O índice do DataFrame deve ser um DatetimeIndex.")
    base = diario.sort_index()
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
    limite = pd.Timestamp(fim_treino)
    if limite.tzinfo is not None:
        limite = limite.tz_convert(None)
    ordenado = df.sort_index()
    treino = ordenado.loc[ordenado.index <= limite]
    teste = ordenado.loc[ordenado.index > limite]
    if treino.empty or teste.empty:
        raise ValueError("A data fim_treino deve deixar treino e teste não vazios.")
    return treino, teste
