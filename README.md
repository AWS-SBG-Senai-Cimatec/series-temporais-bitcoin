# Comparador de Técnicas de Machine Learning para Séries Temporais (Bitcoin)

Projeto do **Time de Projetos e Ações do AWS SBG SENAI CIMATEC**. Desenvolvimento de um comparador
entre técnicas de treinamento de modelos de machine learning para séries temporais, aplicado à
previsão do preço do Bitcoin (BTC/USD), com o objetivo de praticar boas práticas de modelagem e de
ciência de dados.

> Projeto educacional, sem fins lucrativos e com custo zero. Não é recomendação financeira.

## Objetivos

- Comparar técnicas de machine learning (scikit-learn) na previsão do preço de fechamento diário do Bitcoin.
- Praticar validação temporal, ausência de vazamento de dados, comparação com modelos de referência (baselines) e versionamento de modelos.
- Entregar um protótipo funcional (app web em Streamlit) para demonstração em eventos.

## Equipe

| Nome | Papel | GitHub |
|---|---|---|
| Mateus | Líder técnico | @mateuspauperio |
| Lucas | Participante | @(a preencher) |
| Lucca | Participante | @(a preencher) |
| Marcos | Participante | @(a preencher) |

Frentes de trabalho: **A. Dados**, **B. Modelos**, **C. App e visual** (responsáveis a definir na primeira reunião).

## O que será entregue

1. Repositório organizado e documentado (README, `requirements.txt`, `.gitignore`, `src/`, `docs/`).
2. Notebooks com a análise dos dados, os baselines e a comparação dos modelos.
3. Modelos versionados com Joblib.
4. App em Streamlit, a partir de um protótipo no Figma.
5. Material básico no Canva para o time de conteúdo apresentar o projeto em eventos.

## Cronograma

Reunião semanal. Entrega-alvo: 30/11, com margem até 06/12.

| Semana | Período | Foco |
|---|---|---|
| 1 | 26/10 a 01/11 | Kickoff, ambiente e primeiro contato com os dados |
| 2 | 02/11 a 08/11 | Dados diários, análise exploratória, features e baselines |
| 3 | 09/11 a 15/11 | Treino e comparação dos modelos |
| 4 | 16/11 a 22/11 | Ajuste de hiperparâmetros, Joblib e app com as abas básicas |
| 5 | 23/11 a 29/11 | App completo, README e material no Canva |
| 6 | 30/11 a 06/12 | Revisão final, ensaio da demonstração e entrega |

O andamento das tarefas fica na aba **Projects** deste repositório.

## Estrutura do repositório

```
├── data/          dados (não versionados; ver "Dados")
├── docs/          documentação do projeto
├── models/        modelos treinados (.joblib)
├── notebooks/     experimentos e análises
├── src/           código reutilizável
├── CONTRIBUTING.md
├── LICENSE
├── README.md
└── requirements.txt
```

## Como executar

Pré-requisitos: Python 3.10 ou superior, Git e VS Code.

```
git clone https://github.com/AWS-SBG-Senai-Cimatec/series-temporais-bitcoin.git
cd series-temporais-bitcoin
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows (PowerShell)
# source .venv/bin/activate       # macOS / Linux
pip install -r requirements.txt
```

As instruções de uso do projeto serão completadas ao longo do desenvolvimento.

## Dados

Dataset **Bitcoin Historical Data** (Zielak / mczielinski), no Kaggle:
https://www.kaggle.com/datasets/mczielinski/bitcoin-historical-data

São candles de 1 minuto da exchange Bitstamp. O arquivo é grande (cerca de 390 MB) e **não deve ser
enviado ao GitHub**: cada pessoa baixa o seu e coloca na pasta `data/`. Confira a licença e as
condições de uso na página do dataset.

## Como contribuir

Leia o [CONTRIBUTING.md](CONTRIBUTING.md) antes de enviar qualquer alteração.

## Licença

Código sob a licença GPL-3.0 (arquivo `LICENSE`). Os dados têm licença própria, definida pelo Kaggle.
