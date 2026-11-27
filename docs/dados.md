# Dados e reprodução local

## Fonte e arquivos

A fonte é o conjunto [Bitcoin Historical Data](https://www.kaggle.com/datasets/mczielinski/bitcoin-historical-data), de Zielak / mczielinski: candles de um minuto da Bitstamp. Baixe o CSV no Kaggle e mantenha-o localmente. O projeto não distribui nem versiona o arquivo de origem ou a base derivada.

O CSV diário usado pelos notebooks é `data/btc_diario.csv`, com uma linha por dia UTC, índice/coluna `data` e as colunas `open`, `high`, `low`, `close`, `volume`. A origem costuma ter as colunas `Timestamp`, `Open`, `High`, `Low`, `Close` e `Volume_(BTC)`; o timestamp da fonte é Unix em segundos.

## Gerar a base diária

Use Python 3.10 ou superior. Na raiz do repositório, crie e ative um ambiente virtual e instale as dependências:

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
```

Depois de baixar o CSV no Kaggle, rode:

```bash
python preparar_arquivos.py --entrada "C:/caminho/bitcoin_minute.csv"
```

O padrão grava `data/btc_diario.csv`, a partir de `2018-01-01`. O final padrão é o último dia UTC anterior ao dia do último candle no arquivo, para não incluir um dia potencialmente incompleto. É possível escolher o intervalo, sempre com limites inclusivos:

```bash
python preparar_arquivos.py --entrada "C:/caminho/bitcoin_minute.csv" --inicio 2018-01-01 --fim 2024-12-31
```

`--fim` é uma escolha explícita e deve apontar para um dia completo. A agregação ordena os candles por instante UTC e calcula primeiro `open`, máximo `high`, mínimo `low`, último `close` e soma de `volume`. Datas sem candles no intervalo causam erro com a primeira data ausente; o script não interpola nem preenche lacunas. Corrija/obtenha uma fonte completa antes de modelar.

Depois da geração, valide leitura, intervalo e continuidade pela raiz do repositório:

```bash
python -c "from src.features import carregar_diario; d=carregar_diario('data/btc_diario.csv'); assert d.index.equals(__import__('pandas').date_range(d.index.min(), d.index.max(), freq='D')); print(d.shape, d.index.min().date(), d.index.max().date())"
```

Para uma execução reproduzível, registre a versão/data de download da fonte, o intervalo selecionado, a linha de comando e o corte de treino. O agregador não baixa dados, não depende de rede e não produz previsões de exemplo.

## Carregamento e formatos de data

`src/features.py` contém `carregar_diario(caminho)`. Ele aceita `data` ou `Unnamed: 0` como coluna de data, além das colunas OHLCV em minúsculas. A data pode estar em ISO (`2024-03-04`), dia/mês/ano (`04/03/2024`), mês/dia/ano (`03/04/2024`), `AAAAMMDD` numérico ou Unix em segundos/milissegundos. Datas textuais ambíguas seguem a convenção brasileira: `03/04/2024` significa 3 de abril. Timestamps com fuso são convertidos para UTC antes de obter o dia.

A carga valida datas, valores numéricos finitos e colunas obrigatórias, normaliza para um índice diário sem fuso (calendário UTC), ordena e rejeita datas repetidas. Dias ausentes são permitidos na carga para inspeção, mas `criar_features` exige calendário contínuo: sem isso, “próximo dia” poderia virar apenas “próxima linha disponível”.

```python
from src.features import carregar_diario

diario = carregar_diario("data/btc_diario.csv")
print(diario.index.min(), diario.index.max(), diario.shape)
```

## Variáveis, alvo e recorte temporal

`criar_features(diario)` usa informações até o dia `t` para prever o fechamento do dia `t+1`. Produz `close_lag_1`, `close_lag_7`, `close_lag_30`, `volume_lag_1` e `retorno_1d`; linhas sem histórico ou alvo são removidas.

`dividir_treino_teste(df, fim_treino)` ordena cronologicamente, não embaralha e considera inclusivo o dia de corte no treino. O teste começa no dia seguinte. A data pode ser ISO ou uma data textual com convenção brasileira; use ISO para evitar ambiguidade, por exemplo `2024-12-31`. O recorte é feito pela data de origem da previsão. Assim, a linha de origem no corte fica no treino mesmo que seu alvo seja o fechamento do dia seguinte. Fixe o corte antes de comparar modelos.

```python
from src.features import carregar_diario, criar_features, dividir_treino_teste

diario = carregar_diario("data/btc_diario.csv")
X, y = criar_features(diario)
treino, teste = dividir_treino_teste(X.join(y), "2024-12-31")
```

## Arquivos versionados e notebooks

`data/` é ignorada pelo Git, exceto `data/.gitkeep`. Não adicione CSVs de origem/derivados, previsões, dumps, modelos ou cópias dos dados em outra pasta. O script grava apenas a saída solicitada; diretórios de saída personalizados também devem permanecer fora do commit.

- `notebooks/01_exploracao.ipynb`: período, qualidade, estatísticas e gráficos.
- `notebooks/02_features.ipynb`: variáveis, alinhamento do alvo e divisão temporal.

Execute Jupyter a partir da raiz do projeto para que os caminhos documentados funcionem.
