"""Agrega candles Bitstamp do Kaggle em uma base diária reproduzível.

Uso: python preparar_arquivos.py --entrada caminho/bitcoin_minute.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", required=True, type=Path, help="CSV de candles de 1 minuto baixado do Kaggle")
    parser.add_argument("--saida", type=Path, default=Path("data/btc_diario.csv"))
    parser.add_argument("--inicio", default="2018-01-01", help="Primeiro dia UTC (inclusive)")
    parser.add_argument("--fim", help="Último dia UTC (inclusive); padrão: último dia UTC completo do arquivo")
    return parser.parse_args()


def _coluna(df: pd.DataFrame, *nomes: str) -> str:
    por_nome = {str(c).strip().lower(): c for c in df.columns}
    for nome in nomes:
        if nome.lower() in por_nome:
            return por_nome[nome.lower()]
    raise ValueError(f"Não encontrei coluna entre: {', '.join(nomes)}")


def agregar(entrada: Path, saida: Path, inicio: str, fim: str | None) -> pd.DataFrame:
    """Lê timestamps Unix em segundos (formato Kaggle) e agrega dias UTC."""
    if not entrada.is_file():
        raise FileNotFoundError(f"CSV de origem não encontrado: {entrada}")
    bruto = pd.read_csv(entrada)
    data_col = _coluna(bruto, "Timestamp", "timestamp", "Date", "date", "data")
    nomes = {
        "open": _coluna(bruto, "Open", "open"),
        "high": _coluna(bruto, "High", "high"),
        "low": _coluna(bruto, "Low", "low"),
        "close": _coluna(bruto, "Close", "close"),
        "volume": _coluna(bruto, "Volume_(BTC)", "Volume BTC", "volume", "Volume")
    }
    valores = pd.to_numeric(bruto[data_col], errors="coerce")
    if valores.isna().any():
        raise ValueError("A coluna Timestamp contém valores inválidos; o CSV esperado usa Unix em segundos.")
    timestamps = pd.to_datetime(valores, unit="s", utc=True, errors="coerce")
    if timestamps.isna().any():
        raise ValueError("Não foi possível interpretar todos os timestamps Unix.")
    candles = bruto[list(nomes.values())].rename(columns={v: k for k, v in nomes.items()})
    for coluna in nomes:
        candles[coluna] = pd.to_numeric(candles[coluna], errors="coerce")
    if candles.isna().any().any():
        raise ValueError("O CSV contém valores OHLCV ausentes ou não numéricos.")
    candles.index = timestamps
    candles.index.name = "instante_utc"
    candles = candles.sort_index()
    dias = candles.resample("D", label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
    ).dropna()

    inicio_ts = pd.Timestamp(inicio, tz="UTC").normalize()
    if fim:
        fim_ts = pd.Timestamp(fim, tz="UTC").normalize()
    else:
        # Nunca inclui o último dia do arquivo, que pode estar incompleto.
        fim_ts = candles.index.max().normalize() - pd.Timedelta(days=1)
    if fim_ts < inicio_ts:
        raise ValueError("O fim informado é anterior ao início.")
    dias = dias.loc[(dias.index >= inicio_ts) & (dias.index <= fim_ts)]
    esperado = pd.date_range(inicio_ts, fim_ts, freq="D", tz="UTC")
    dias = dias.reindex(esperado)
    if dias.isna().any().any():
        faltantes = dias.index[dias.isna().any(axis=1)]
        raise ValueError(f"Há dias sem candles no intervalo: {faltantes[0].date()} (e possivelmente outros). Não preenchi lacunas automaticamente.")
    dias.index = dias.index.tz_localize(None)
    dias.index.name = "data"
    saida.parent.mkdir(parents=True, exist_ok=True)
    dias.to_csv(saida, date_format="%Y-%m-%d", float_format="%.10g")
    return dias


def main() -> None:
    args = argumentos()
    diario = agregar(args.entrada, args.saida, args.inicio, args.fim)
    print(f"Base diária gravada em {args.saida}: {len(diario):,} dias")
    print(f"Período UTC: {diario.index.min().date()} a {diario.index.max().date()}")


if __name__ == "__main__":
    main()
