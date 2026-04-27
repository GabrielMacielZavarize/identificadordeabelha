# Guia dos Desenvolvedores

Este guia mostra o fluxo que todo desenvolvedor deve seguir no projeto.

A ideia e simples:

```text
voce cria sua branch -> faz sua tarefa -> abre PR para develop
```

Depois disso, Gabriel cuida de homologacao (`staging`) e producao (`main`).

## 1. O que cada branch significa

| Branch | Para que serve | Quem usa |
|--------|----------------|----------|
| `develop` | Desenvolvimento do dia a dia | Time |
| `staging` | Homologacao/teste antes de producao | Gabriel |
| `main` | Producao | Gabriel |

Regras principais:

- Todo trabalho novo comeca na `develop`.
- Desenvolvedor abre Pull Request sempre para `develop`.
- Nao faca push direto em `staging`.
- Nao faca push direto em `main`.
- Nao abra Pull Request direto para `main`, a menos que Gabriel peça.

## 2. Antes de comecar

Abra o terminal dentro da pasta do projeto.

Se estiver usando Linux ou macOS:

```bash
cd caminho/para/identificadordeabelha
```

Se estiver usando Windows com Git Bash, use algo parecido com:

```bash
cd /c/caminho/para/identificadordeabelha
```

Confirme se voce esta dentro do repositorio:

```bash
git status
```

Se aparecer algo como `On branch develop` ou `On branch alguma-coisa`, esta certo.

## 3. Atualizar a develop

Antes de criar qualquer branch, sempre atualize a `develop`:

```bash
git checkout develop
git pull origin develop
```

O que isso faz:

- `git checkout develop`: entra na branch `develop`.
- `git pull origin develop`: baixa as ultimas mudancas do GitHub.

Se o comando `git pull` mostrar erro, pare e peca ajuda antes de continuar.

## 4. Criar sua branch de trabalho

Crie uma branch com nome claro:

```bash
git checkout -b CARD-[01]
```

Exemplo Padrão:

```text
CARD-[ID]
```

## 5. Trabalhar nos arquivos

Edite os arquivos normalmente no VS Code ou outro editor.

Depois de alterar, veja o que mudou:

```bash
git status
```

Para ver diferencas no terminal:

```bash
git diff
```

Se quiser sair da tela do diff, aperte `q`.

## 6. Rodar o frontend localmente

Entre na pasta do frontend:

```bash
cd frontend
```

Instale as dependencias se for a primeira vez:

```bash
npm install
```

Rode o projeto:

```bash
npm run dev
```

Abra no navegador:

```text
http://localhost:5173
```

Para parar o servidor, volte no terminal e aperte:

```text
Ctrl + C
```

Depois volte para a raiz do projeto:

```bash
cd ..
```

## 7. Rodar checagens do frontend

Antes de abrir Pull Request, rode:

```bash
cd frontend
npm run lint
npm run build
npm run test
cd ..
```

O que cada comando faz:

- `npm run lint`: procura erros de padrao e codigo.
- `npm run build`: confirma se o frontend compila.
- `npm run test`: roda os testes automatizados.

Se algum comando der erro vermelho, corrija antes de abrir PR.

## 8. Rodar backend localmente com Docker

Na raiz do projeto:

```bash
docker compose up --build
```

Isso sobe os servicos de desenvolvimento.

Normalmente:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8001`

Para parar:

```text
Ctrl + C
```

Se precisar parar tudo depois:

```bash
docker compose down
```

## 9. Rodar testes do backend

Se voce tiver ambiente Python configurado:

```bash
cd backend
python -m pytest
cd ..
```

Em alguns computadores o comando pode ser:

```bash
cd backend
python3 -m pytest
cd ..
```

Se aparecer erro dizendo que `pytest` nao existe, seu ambiente Python ainda nao esta preparado. Nesse caso, avise no PR que os testes do backend serao validados pelo CI do GitHub.

## 10. Fazer commit

Veja quais arquivos mudaram:

```bash
git status
```

Adicione os arquivos que voce quer commitar:

```bash
git add caminho/do/arquivo
```

Exemplo:

```bash
git add frontend/src/App.tsx
git add docs/guia-desenvolvedores.md
```

Se tiver certeza que quer adicionar tudo que mudou:

```bash
git add .
```

Agora crie o commit:

```bash
git commit -m "Add history page filters"
```

## 11. Enviar sua branch para o GitHub

Na primeira vez que enviar sua branch:

```bash
git push -u origin feature/nome-da-tarefa
```

Depois disso, se fizer novos commits na mesma branch, basta:

```bash
git push
```

## 12. Abrir Pull Request

No GitHub, abra o repositorio e clique em:

```text
Compare & pull request
```

Configure assim:

```text
base: develop
compare: sua-branch
```

Exemplo:

```text
base: develop
compare: feature/tela-historico
```

No titulo, escreva algo claro:

```text
Add history page filters
```

Na descricao, use este modelo:

```md
## O que foi feito
-

## Como testar
-

## Observacoes
- Mudou variavel de ambiente? Nao
- Criou migration? Nao
- Tem algo pendente? Nao
```

## 13. Depois de abrir o PR

Aguarde o CI terminar.

O CI e o teste automatico do GitHub. Ele roda:

- `Backend tests`
- `Frontend tests`

Se ficar verde, esta bom.

Se ficar vermelho:

1. Clique no check que falhou.
2. Leia o erro.
3. Corrija na sua branch.
4. Faca novo commit.
5. Envie novamente com `git push`.

Exemplo:

```bash
git add .
git commit -m "Fix failing frontend test"
git push
```

O Pull Request atualiza sozinho.

## 14. Se a develop mudou enquanto voce trabalhava

Atualize sua branch com a `develop`:

```bash
git checkout develop
git pull origin develop
git checkout feature/nome-da-tarefa
git merge develop
```

Se aparecer conflito, nao tente resolver no chute. Chame Gabriel ou alguem mais experiente.

## 15. Depois que o PR for mergeado

Volte para `develop`:

```bash
git checkout develop
git pull origin develop
```

Apague sua branch local:

```bash
git branch -d feature/nome-da-tarefa
```

Se quiser apagar a branch remota pelo GitHub, use o botao `Delete branch` que aparece depois do merge.

## 16. O que nunca enviar para o GitHub

Nao commite:

```text
.env
.env.local
backend/.env
node_modules/
frontend/dist/
.venv/
*.sqlite
data/uploads/*
artifacts/models/*
```

Esses arquivos podem ter segredo, dados locais, arquivos grandes ou coisas geradas automaticamente.

Se precisar adicionar uma nova variavel, edite somente:

```text
.env.example
backend/.env.example
```

## 17. Resumo rapido

Fluxo normal:

```bash
git checkout develop
git pull origin develop
git checkout -b feature/nome-da-tarefa
```

Depois de editar:

```bash
git status
git add .
git commit -m "Mensagem clara"
git push -u origin feature/nome-da-tarefa
```

No GitHub:

```text
Abrir PR para develop
Aguardar CI
Corrigir se falhar
Esperar merge
```
