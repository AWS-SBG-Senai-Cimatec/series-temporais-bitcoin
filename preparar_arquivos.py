from pathlib import Path
import numpy as np
import pandas as pd

# Cria a pasta temporária para o grupo caso ela não exista
Path("para_o_grupo").mkdir(exist_ok=True)

# Gera datas diárias de exemplo a partir de 2018-01-01 até hoje
datas = pd.date_range(start="2018-01-01", end="2026-11-12", freq="D")
rng = np.random.default_rng(42)

# Simula uma série de preço do Bitcoin realista para testes
precosbase = 10000 + np.cumsum(rng.normal(5, 100, len(datas)))
precosbase = np.maximum(precosbase, 100) # Evita valores negativos

d = pd.DataFrame({
    "open": precosbase * (1 + rng.normal(0, 0.002, len(datas))),
    "high": precosbase * (1 + abs(rng.normal(0.005, 0.005, len(datas)))),
    "low": precosbase * (1 - abs(rng.normal(0.005, 0.005, len(datas)))),
    "close": precosbase,
    "volume": rng.uniform(10, 1000, len(datas))
}, index=datas)
d.index.name = "data"

# Salva o arquivo diário oficial para o grupo
d.to_csv("para_o_grupo/btc_diario.csv")

# 2) Geração de previsões de exemplo para o time testar o app/gráficos
p = pd.DataFrame({"real": d["close"], "naive": d["close"].shift(1)})
p["modelo_exemplo"] = p["naive"] * (1 + rng.normal(0, 0.01, len(p)))
p = p.dropna().loc["2025-01-01":]
p.to_csv("para_o_grupo/previsoes_exemplo.csv")

print("--- ARQUIVOS GERADOS COM SUCESSO ---")
print(f"Dados diários: {d.shape} | Período: {d.index.min().date()} a {d.index.max().date()}")
print(f"Previsões de exemplo: {p.shape} | Período: {p.index.min().date()} a {p.index.max().date()}")