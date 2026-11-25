# Conceitos da modelagem

Este documento explica, de forma simples, os conceitos usados na frente de Modelos do projeto.

## O problema

O projeto prevê o preço de fechamento (`close`) do Bitcoin no dia seguinte, em dólares, a partir do histórico diário de preços e volume (arquivo `btc_diario.csv`, de 2018 em diante). Cada linha dos dados tem o preço de hoje, e o alvo é o preço de amanhã.

## Divisão temporal

Em uma série temporal, a ordem dos dias importa: o preço de hoje depende do que aconteceu antes. Por isso os dados são divididos no tempo: o modelo treina com o passado (de 2018 até a data de corte) e é testado no futuro (depois da data de corte).

Os dados nunca são embaralhados. Se fossem, o modelo poderia treinar com dias de 2026 e ser testado em dias de 2020, ou seja, "veria o futuro" durante o treino. O erro medido ficaria artificialmente baixo e não mostraria como o modelo se sairia em dias realmente novos.

A data de fim do treino é fixada, para que todos os modelos sejam comparados no mesmo período de teste. Nos primeiros testes foi usada a data provisória 31/12/2024.

Nos primeiros testes foi usada a data provisória 31/12/2024, o que deixou 2527 dias para treino e 680 para teste. Os 30 primeiros dias saem do treino porque a variável `close_lag_30` precisa de 30 dias de histórico.


## Variáveis e alvo

Um modelo recebe **variáveis** (também chamadas de *features*, as "pistas") e tenta acertar o **alvo** (a "resposta"). Por convenção, as variáveis ficam em `X` e o alvo em `y`.

Neste projeto, cada linha de `X` descreve o que se sabe em um dia, e o `y` dessa linha é o preço de fechamento do dia seguinte. As variáveis são *lags* (valores de dias anteriores):

| Variável | O que é |
|---|---|
| `close_lag_1` | fechamento de hoje |
| `close_lag_7` | fechamento de 7 dias atrás |
| `close_lag_30` | fechamento de 30 dias atrás |
| `volume_lag_1` | volume negociado hoje |
| `retorno_1d` | variação percentual do preço no dia |

Todas usam apenas informação até hoje, para evitar vazamento de dados. As funções que as criam ficam em `src/features.py`.

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


## Modelos

Um modelo é uma fórmula que aprende com exemplos. No treino (`fit`), ele recebe as variáveis e as respostas certas do passado e se ajusta para errar pouco. Na previsão (`predict`), recebe só as variáveis de dias novos e devolve a sua estimativa do alvo. Todos os modelos do scikit-learn seguem esse mesmo padrão.

Dois termos importantes: **pesos** são os valores que o modelo aprende sozinho durante o treino, e **hiperparâmetros** são configurações que nós escolhemos antes do treino.

### Regressão Linear

Faz uma soma ponderada das variáveis: previsão = peso1 × variável1 + peso2 × variável2 + ... No treino, escolhe os pesos que deixam o erro menor.

### Ridge

É uma Regressão Linear com uma penalidade para pesos grandes. A força da penalidade é o hiperparâmetro `alpha`: com `alpha = 0` é igual à Regressão Linear, e com um valor muito grande os pesos ficam quase zerados. Ajuda a evitar o overfitting. Usamos `alpha = 1.0` como valor inicial.

### KNN

Para prever um dia, procura no treino os `k` dias mais parecidos (pela distância entre as variáveis) e faz a média do alvo desses dias. Usamos `k = 5`. O KNN não monta uma fórmula: ele guarda os dias do treino. Por isso só consegue devolver valores dentro da faixa que viu no treino, e é sensível à escala das variáveis (o preço vale dezenas de milhares, e o `retorno_1d` fica perto de 0,01).


## Prever o preço ou a variação

O preço do Bitcoin subiu ao longo dos anos: no treino, o maior fechamento foi cerca de 15.138, e no teste chegou a cerca de 20.099. O KNN só devolve médias de valores que viu no treino, então, ao prever o preço, ficou preso perto do teto do treino nos dias mais caros e errou muito (MAE de 1789 dólares).

A solução foi prever a **variação** (preço de amanhã menos o de hoje) e depois somar o preço de hoje de volta. As variações têm tamanho mais estável ao longo do tempo, e o MAE caiu para 92 dólares. A lição é que, quando o alvo muda de nível com o tempo, modelos que não extrapolam precisam prever mudanças, e não níveis. Modelos de árvore têm a mesma limitação do KNN.

## Overfitting

Overfitting é quando o modelo "decora" o treino: acerta bem nos dias que já viu e erra em dias novos. Por isso o erro é sempre medido no teste. O Ridge e a escolha cuidadosa dos hiperparâmetros são formas de reduzir esse risco.

## Comparação dos modelos (parcial)

Resultados no período de teste (corte provisório em 31/12/2024):

| Modelo | MAE (US$) | RMSE (US$) | MAPE (%) |
|---|---|---|---|
| Naive | 80,43 | 99,68 | 0,50 |
| Regressão Linear | 82,08 | 101,92 | 0,51 |
| Ridge (`alpha = 1.0`) | 82,07 | 101,92 | 0,51 |
| KNN (prevendo o preço) | 1789,36 | 2498,00 | 9,87 |
| KNN (prevendo a variação) | 92,03 | 115,43 | 0,57 |

Nenhum modelo superou o naive até agora. Uma explicação provável é que o preço de hoje já contém quase toda a informação útil para prever o de amanhã, e as outras variáveis acrescentam pouco.

## Ajuste de hiperparâmetros

Até aqui foram usados valores iniciais (`alpha = 1.0` e `k = 5`), sem ajuste. Ajustar é testar vários valores e escolher o que dá o menor erro. Em séries temporais, esse teste não pode embaralhar os dados.






