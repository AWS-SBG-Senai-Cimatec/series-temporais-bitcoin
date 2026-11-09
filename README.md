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

| Nome | Papel | Área inicial | GitHub |
|---|---|---|---|
| Mateus | Líder técnico | Coordenação, revisão e integração | @mateuspauperio |
| Lucas Merces | Participante | Dados | @lucasmoraismerces |
| Lucca | Participante | Modelos | @devluccam |
| Marcos | Participante | App e visual | @mszporer03-a11y |

Cada pessoa é responsável principal por uma área, mas todos participam de todas as etapas e podem
ajudar uns aos outros. A divisão pode mudar ao longo do projeto.

## Como o trabalho está organizado

- **Reunião semanal, às quartas-feiras.**
- **Nas reuniões,** o grupo trabalha junto nos pontos que destravam os demais (por exemplo, a construção dos dados diários).
- **Entre as reuniões,** cada pessoa avança em tarefas da sua área, em paralelo, com base nos combinados entre as áreas (formatos de arquivos, nomes de funções e formato das tabelas), registrados em [docs/combinados.md](docs/combinados.md).
- **Todo trabalho entra por pull request,** revisado pelo líder, de modo que a branch `main` esteja sempre funcionando.

## O que será entregue

1. Repositório organizado e documentado (README, `requirements.txt`, `.gitignore`, `src/`, `docs/`).
2. Notebooks com a análise dos dados, os baselines e a comparação dos modelos.
3. Modelos versionados com Joblib.
4. App em Streamlit, a partir de um protótipo no Figma.
5. Material básico no Canva para o time de conteúdo apresentar o projeto em eventos.

## Cronograma

| Reunião | Data | Foco |
|---|---|---|
| 1 | 11/11 | Apresentação, dados diários em conjunto e combinados entre as áreas |
| 2 | 18/11 | Integração de variáveis, métricas e baselines; início do treino dos modelos |
| 3 | 25/11 | Comparação dos modelos, salvamento com Joblib e app com os modelos |
| 4 | 02/12 | Revisão final e ensaio da demonstração |
| Entrega | até 06/12 | Execução do projeto do zero, versão final e material no Canva |

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

Leia o [CONTRIBUTING.md](CONTRIBUTING.md) antes de enviar qualquer alteração e consulte os
[combinados entre as áreas](docs/combinados.md).

## Licença

Código sob a licença GPL-3.0 (arquivo `LICENSE`). Os dados têm licença própria, definida pelo Kaggle.
