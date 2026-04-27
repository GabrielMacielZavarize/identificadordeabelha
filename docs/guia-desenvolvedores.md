# Guia dos Desenvolvedores

Este guia explica o fluxo que todo desenvolvedor deve seguir no projeto.

## Branches do projeto

| Branch | Uso | Quem mexe |
|--------|-----|-----------|
| `develop` | Desenvolvimento do dia a dia | Time de desenvolvimento |
| `staging` | Homologacao | Somente via Pull Request aprovado |
| `main` | Producao | Somente via Pull Request aprovado |

Use `develop` como base para qualquer trabalho novo.

Nao faca push direto em `staging` ou `main`.

## Antes de comecar

Atualize sua branch local:

```bash
git checkout develop
git pull origin develop
```

Crie uma branch para sua tarefa:

```bash
git checkout -b feature/nome-da-tarefa
```

Exemplos de nomes:

```text
feature/tela-historico
feature/cadastro-especies
fix/corrigir-upload-imagem
docs/atualizar-readme
```

## Durante o desenvolvimento

Faca commits pequenos e com mensagens claras:

```bash
git status
git add caminho/do/arquivo
git commit -m "Add species form validation"
```

Evite commits muito grandes misturando assuntos diferentes.

## O que nunca commitar

Nao envie arquivos com segredo, configuracao local ou dados grandes:

```text
.env
*.sqlite
data/uploads/*
artifacts/models/*
node_modules/
.venv/
```

Se precisar de uma variavel nova, atualize apenas o arquivo de exemplo:

```text
.env.example
backend/.env.example
```

## Antes de abrir o Pull Request

Atualize sua branch com a `develop`:

```bash
git checkout develop
git pull origin develop
git checkout feature/nome-da-tarefa
git merge develop
```

Rode os testes que conseguir localmente:

```bash
cd frontend
npm run lint
npm run build
npm run test
```

Se mexeu no backend e tiver ambiente Python configurado:

```bash
cd backend
python -m pytest
```

## Enviar para o GitHub

Envie sua branch:

```bash
git push -u origin feature/nome-da-tarefa
```

Abra um Pull Request no GitHub:

```text
feature/nome-da-tarefa -> develop
```

No PR, escreva:

- O que foi feito.
- Como testar.
- Se mudou alguma variavel de ambiente.
- Se criou migration, script ou dependencia nova.

## Depois de abrir o PR

Aguarde o CI terminar.

Se o CI ficar vermelho:

1. Clique no job que falhou.
2. Leia o erro.
3. Corrija na sua branch.
4. Faca novo commit e push.

Exemplo:

```bash
git add .
git commit -m "Fix failing test"
git push
```

O GitHub atualiza o PR automaticamente.

## Depois que o PR for mergeado

Volte para `develop` e atualize:

```bash
git checkout develop
git pull origin develop
```

Remova sua branch local se nao precisar mais dela:

```bash
git branch -d feature/nome-da-tarefa
```

## Regras importantes

- Trabalhe sempre a partir da `develop`.
- Abra PR sempre para `develop`.
- Nao abra PR direto para `staging` ou `main`, a menos que Gabriel peça.
- Nao faca force push em branch compartilhada.
- Nao altere configuracoes de homologacao ou producao sem alinhar antes.
- Nao coloque segredo em commit.

