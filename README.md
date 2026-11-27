# Séries temporais do Bitcoin

Projeto de análise e previsão do fechamento diário do Bitcoin com dados da Bitstamp.

## Rodar localmente

1. Crie um ambiente Python 3.10+ e instale `requirements.txt`.
2. Baixe o CSV de candles de um minuto do [Bitcoin Historical Data no Kaggle](https://www.kaggle.com/datasets/mczielinski/bitcoin-historical-data).
3. Gere a base diária na raiz do projeto:

   ```bash
   python preparar_arquivos.py --entrada "caminho/bitcoin_minute.csv"
   ```

4. Abra os notebooks a partir da raiz. Eles leem `data/btc_diario.csv`.

Veja [docs/dados.md](docs/dados.md) para instalação, formatos de data aceitos, intervalo, agregação, dias incompletos, validações e regras de versionamento. A pasta `data/` e os arquivos gerados em `models/` são locais e ignorados pelo Git.
