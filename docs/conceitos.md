# Conceitos da modelagem

Este documento explica, de forma simples, os conceitos usados na frente de Modelos do projeto.

## O problema

O projeto prevê o preço de fechamento (`close`) do Bitcoin no dia seguinte, em dólares, a partir do histórico diário de preços e volume (arquivo `btc_diario.csv`, de 2018 em diante). Cada linha dos dados tem o preço de hoje, e o alvo é o preço de amanhã.

## Divisão temporal

Em uma série temporal, a ordem dos dias importa: o preço de hoje depende do que aconteceu antes. Por isso os dados são divididos no tempo: o modelo treina com o passado (de 2018 até a data de corte) e é testado no futuro (depois da data de corte).

Os dados nunca são embaralhados. Se fossem, o modelo poderia treinar com dias de 2026 e ser testado em dias de 2020, ou seja, "veria o futuro" durante o treino. O erro medido ficaria artificialmente baixo e não mostraria como o modelo se sairia em dias realmente novos.

A data de fim do treino é fixada, para que todos os modelos sejam comparados no mesmo período de teste. Nos primeiros testes foi usada a data provisória 31/12/2024.

## Vazamento de dados

Vazamento de dados acontece quando o modelo recebe, sem querer, informação que ele não teria na hora de fazer a previsão real. Ele "cola" a resposta, e o resultado parece bom demais.

Neste projeto, um exemplo seria usar o preço de amanhã como variável para prever o preço de amanhã. Outro seria calcular uma média que inclua dias futuros. Por isso, todas as variáveis são criadas apenas com informações do passado e a divisão treino/teste respeita a ordem do tempo.

## Baseline

Baseline é um modelo de referência que serve de régua. O baseline mais básico é o naive: a previsão de amanhã é simplesmente o preço de hoje.

Um modelo mais complexo só se justifica se errar menos que o baseline no mesmo período de teste. Se não errar, o modelo simples vence e a complexidade não valeu a pena.

Resultados dos baselines no período de teste (a partir de 01/01/2025, data de corte provisória):

| Baseline | MAE (US$) | RMSE (US$) | MAPE (%) |
|---|---|---|---|
| Naive (amanhã = hoje) | 80,43 | 99,68 | 0,50 |
| Média móvel de 7 dias | 138,27 | 169,01 | 0,85 |

O naive errou menos que a média de 7 dias em todas as métricas. A média usa preços de até uma semana atrás e, por isso, fica "atrasada" em relação ao preço de hoje, que é a informação mais recente. Qualquer modelo treinado precisa bater o MAE de 80,43 para se justificar.

## Métricas de erro

As métricas medem o tamanho do erro entre o preço real e o previsto. Quanto menor, melhor. Elas são calculadas sempre no período de teste, que o modelo não viu no treino.

- **MAE** (erro absoluto médio): em média, quantos dólares o modelo errou por dia.
- **RMSE** (raiz do erro quadrático médio): parecido com o MAE, mas erros grandes pesam mais. Se o RMSE for bem maior que o MAE, o modelo tem alguns dias de erro muito grande.
- **MAPE** (erro percentual absoluto médio): o erro médio em porcentagem do preço real. Ajuda a comparar erros quando o preço muda muito ao longo dos anos.

No código, as três são calculadas pela função `metricas(y_real, y_prev)`, em `src/metricas.py`.



