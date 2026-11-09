# Combinados entre as áreas

Este documento registra os formatos e os nomes que ligam as áreas do projeto. Foi escrito como
rascunho e deve ser validado pelo grupo na reunião 1 (11/11). Qualquer mudança nele deve ser
comunicada ao grupo e feita por pull request.

## 1. Dados diários

- Arquivo: `data/btc_diario.csv` (gerado localmente; não é enviado ao GitHub).
- Uma linha por dia (UTC), com a coluna `data` como índice e as colunas `open`, `high`, `low`, `close` e `volume`.
- Período de análise: [definir na reunião 1; sugestão: a partir de 2018-01-01].
- Um dia incompleto (por exemplo, o dia atual) não entra nos dados.

## 2. Funções de `src/features.py` (nomes sugeridos)

| Função | O que faz |
|---|---|
| `carregar_diario(caminho)` | Lê o CSV diário e devolve um DataFrame |
| `criar_features(diario)` | Devolve as variáveis e o alvo |
| `dividir_treino_teste(df, fim_treino)` | Divide os dados no tempo, sem embaralhar |

Regras: usar apenas informações do passado para criar as variáveis (sem vazamento de dados) e fixar
a data de fim do treino para que a divisão não mude.
Alvo: [definir na reunião 2; a primeira tentativa pode ser o preço de fechamento do dia seguinte].

## 3. Métricas (`src/metricas.py`)

Função `metricas(y_real, y_prev)`, que devolve um dicionário com `MAE`, `RMSE` e `MAPE_%`.

## 4. Tabela de previsões (usada pelo aplicativo)

Colunas: `data`, `real`, `naive` e uma coluna por modelo. A coluna `data` é o dia do preço previsto.
Os valores são em dólares.

## 5. Modelos salvos

- Arquivos em `models/`, com a versão no nome: `<nome>_v<N>.joblib`.
- `models/registro.json`, com `nome`, `versao`, `arquivo`, `metricas`, `periodo_treino` e `data_treino`.

## 6. Notebooks e responsáveis

Cada notebook tem um único responsável. Funções reutilizáveis ficam em `src/`.

| Notebook | Responsável | Conteúdo |
|---|---|---|
| `01_exploracao` | Lucas | Dados diários e análise exploratória |
| `02_features` | Lucas | Variáveis, alvo e divisão treino/teste |
| `03_baselines` | Lucca | Baselines e métricas |
| `04a_lineares_e_knn` | Lucca | Regressão Linear, Ridge e KNN |
| `04b_modelos_arvores` | Lucas | Random Forest e Gradient Boosting |
| `05_comparacao_e_salvamento` | Lucca | Comparação dos modelos, ajuste (se houver tempo) e Joblib |

O aplicativo (`app.py`), o protótipo no Figma e o material no Canva são de responsabilidade do Marcos.

## 7. Fluxo de trabalho

Branch por tarefa, pull request revisado pelo líder e merge no `main`. Detalhes no
[CONTRIBUTING.md](../CONTRIBUTING.md).
