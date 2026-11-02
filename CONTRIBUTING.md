# Como contribuir

Todo mundo trabalha em **branches** e envia as alterações por **pull request** (PR). O líder técnico
revisa e aprova. Assim o `main` fica sempre funcionando e todo mundo aprende a revisar código.

## Fluxo de trabalho

1. Escolha uma tarefa (issue) no quadro da aba **Projects** e avise no grupo que vai pegá-la.
2. Atualize o seu repositório local:
   ```
   git checkout main
   git pull
   ```
3. Crie uma branch para a tarefa, com o nome no formato `frente/descricao-curta`:
   ```
   git checkout -b dados/eda-inicial
   ```
4. Trabalhe e faça commits pequenos e claros:
   ```
   git add .
   git commit -m "dados: agrega os candles de 1 minuto para dados diarios"
   ```
5. Envie a branch e abra um pull request pelo GitHub:
   ```
   git push -u origin dados/eda-inicial
   ```
6. Preencha o modelo do PR, peça a revisão do líder e responda aos comentários.
7. Depois do merge, volte ao `main`, atualize (`git pull`) e apague a branch local
   (`git branch -d dados/eda-inicial`).

## Regras

- **Nunca** envie dados grandes (a pasta `data/` é ignorada), senhas, chaves ou arquivos pessoais.
- **Cada notebook tem um responsável.** Não edite o notebook de outra pessoa sem combinar antes (o Git
  não consegue juntar alterações de dois autores no mesmo notebook).
- Antes de abrir o PR, execute o notebook inteiro (**Restart & Run All**) para garantir que ele roda do
  começo ao fim sem erros.
- Código reutilizável (funções) vai para `src/`; experimentos e análises ficam em `notebooks/`.
- Escreva README e documentação em português, de forma simples.
- Dúvidas e bloqueios: avise no grupo. Pedir ajuda cedo faz parte do processo.

## Nomes de frentes (prefixo das branches e dos commits)

| Prefixo | Frente |
|---|---|
| `dados` | Dados: download, análise exploratória, features |
| `modelos` | Modelos: baselines, treino, ajuste, Joblib |
| `app` | App Streamlit e protótipo no Figma |
| `docs` | Documentação, README e material para o Canva |
