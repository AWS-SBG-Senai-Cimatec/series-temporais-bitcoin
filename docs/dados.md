# Dados e preparação

## Fonte e armazenamento

O projeto usa o conjunto **Bitcoin Historical Data**, de Zielak / mczielinski, disponível no [Kaggle](https://www.kaggle.com/datasets/mczielinski/bitcoin-historical-data). Ele contém candles de 1 minuto da exchange Bitstamp. Baixe os dados manualmente e mantenha os arquivos localmente; a pasta `data/` não deve ser enviada ao GitHub.

Para a análise, o projeto consome `data/btc_diario.csv`: uma linha por dia, em UTC, com `data` e as colunas `open`, `high`, `low`, `close` e `volume`. O dia corrente, ainda incompleto, deve ser removido. A agregação esperada é: primeiro `open`, máximo `high`, mínimo `low`, último `close` e soma de `volume` em cada dia UTC. Registre junto ao script de preparação a origem, o intervalo de candles e o tratamento de dias incompletos. `preparar_arquivos.py` no estado atual gera dados sintéticos de apoio; não é o agregador do CSV oficial.

## Carga

`src/features.py` oferece `carregar_diario(caminho)`. A função valida o arquivo, converte `data` para índice temporal diário, converte OHLCV para valores numéricos, ordena a série e sinaliza colunas, datas ou valores inválidos. O índice fica sem fuso após a interpretação em UTC, preservando a data do calendário UTC. Datas duplicadas são rejeitadas. Dias ausentes são diagnosticados no notebook exploratório e impedem `criar_features`, porque sem tratamento explícito o alvo da próxima linha poderia não ser o fechamento do dia seguinte.

Exemplo, a partir da raiz do repositório:

```python
from src.features import carregar_diario

diario = carregar_diario("data/btc_diario.csv")
```

## Variáveis e alvo

`criar_features(diario)` exige índice `DatetimeIndex` diário contínuo e colunas `close` e `volume`; produz um par `(X, y)`. Cada linha de `X` representa o instante em que a previsão seria feita, usando somente dados conhecidos até aquela data. As variáveis iniciais são fechamento defasado em 1, 7 e 30 dias, volume defasado em 1 dia e retorno de fechamento em 1 dia. `y` é o fechamento do dia seguinte, alinhado à data de origem da previsão. As linhas sem histórico suficiente ou sem alvo são descartadas.

O alvo de fechamento do próximo dia é a primeira definição de trabalho, conforme os combinados do projeto; deve ser revisto pelo grupo antes da comparação final de modelos.

## Divisão temporal

`dividir_treino_teste(df, fim_treino)` ordena os dados e divide sem embaralhar. A data informada é inclusiva no treino; as datas posteriores ficam no teste. O limite deve ser fixado e documentado na análise para permitir reproduzir os resultados. Como as linhas de `X` usam data de origem e `y` contém o fechamento seguinte, a separação é feita pela data em que a previsão é emitida.

## Notebooks

- `notebooks/01_exploracao.ipynb`: inspeção da série diária, qualidade, período, estatísticas e gráficos exploratórios.
- `notebooks/02_features.ipynb`: criação de variáveis e alvo, conferência do alinhamento e divisão temporal.

Os notebooks esperam `data/btc_diario.csv` na raiz do repositório. Não versionar o dataset nem resultados que possam conter cópias dos dados.
