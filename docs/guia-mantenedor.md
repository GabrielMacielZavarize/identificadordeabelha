# Guia do Mantenedor

Este guia e para Gabriel, responsavel por homologacao (`staging`) e producao (`main`).

## Visao geral do fluxo

```text
feature/* -> develop -> staging -> main
```

O time trabalha em branches `feature/*` ou `fix/*` e abre PR para `develop`.

Voce controla as promocoes:

- `develop -> staging`: vai para homologacao.
- `staging -> main`: vai para producao.

## Quando um desenvolvedor abrir PR para `develop`

Confira:

1. O PR esta indo para `develop`.
2. O titulo explica a mudanca.
3. A descricao tem o que foi feito e como testar.
4. O CI terminou verde.
5. Nao ha `.env`, secrets, dados grandes ou arquivos gerados indevidos.
6. Se houver mudanca de banco, existe migration e instrucao clara.

Se estiver tudo certo, faca merge.

Para PRs pequenos, `Squash and merge` costuma deixar o historico mais limpo.

Depois do merge, remova a branch do PR se o GitHub oferecer essa opcao.

## Quando `develop` estiver pronto para homologacao

Abra um PR:

```text
develop -> staging
```

Se voce quiser ser a pessoa que aprova esse PR, peca para outro colaborador abrir o PR quando voce autorizar. Assim Gabriel fica como aprovador e responsavel pelo merge.

Use um titulo parecido com:

```text
Release staging - YYYY-MM-DD
```

Na descricao, coloque um resumo:

```md
## Mudancas
- ...

## Como validar
- ...

## Observacoes
- Variaveis de ambiente:
- Migrations:
- Riscos:
```

Antes de mergear para `staging`, confirme:

- CI verde.
- Pelo menos 1 aprovacao, se a regra estiver exigindo review.
- Homologacao esta pronta para receber a versao.

Depois do merge, valide em staging.

## Quando staging estiver validado para producao

Abra um PR:

```text
staging -> main
```

Se voce quiser ser a pessoa que aprova esse PR, peca para outro colaborador abrir o PR quando voce autorizar. O importante e que Gabriel revise, aprove e faca o merge para producao.

Use um titulo parecido com:

```text
Release production - YYYY-MM-DD
```

Antes de mergear para `main`, confirme:

- CI verde.
- Staging foi validado.
- Nao ha pendencia conhecida bloqueante.
- Migrations necessarias foram planejadas.
- Variaveis de ambiente de producao estao configuradas.
- Existe plano simples de rollback, se necessario.

Depois do merge em `main`, acompanhe o deploy ou subida de producao.

## Como Gabriel deve commitar as proprias mudancas

Mesmo sendo mantenedor, nao trabalhe direto em `staging` ou `main`.

Comece sempre da `develop`:

```bash
git checkout develop
git pull origin develop
git checkout -b feature/minha-mudanca
```

Faca os commits:

```bash
git add .
git commit -m "Describe my change"
git push -u origin feature/minha-mudanca
```

Abra PR:

```text
feature/minha-mudanca -> develop
```

Quando o CI passar, mergeie em `develop`.

Depois siga o fluxo normal:

```text
develop -> staging -> main
```

## Ponto importante sobre aprovar a propria mudanca

O GitHub normalmente nao conta a aprovacao do proprio autor do PR como review valido.

Isso significa:

- Se Gabriel abriu o PR `develop -> staging`, talvez o GitHub nao deixe Gabriel aprovar esse mesmo PR.
- Se Gabriel abriu o PR `staging -> main`, talvez o GitHub tambem nao deixe Gabriel aprovar esse mesmo PR.

Para manter protecao real, o melhor caminho e ter outro colaborador confiavel para aprovar PRs de release quando a mudanca for sua.

## Modo recomendado com time

Para mudancas feitas por desenvolvedores:

1. Dev abre PR `feature/* -> develop`.
2. Gabriel revisa e mergeia em `develop`.
3. Quando Gabriel autorizar homologacao, um colaborador abre PR `develop -> staging`.
4. Gabriel aprova e mergeia em `staging`.
5. Depois da homologacao, um colaborador abre PR `staging -> main` quando Gabriel autorizar producao.
6. Gabriel aprova e mergeia em `main`.

Esse fluxo funciona bem porque o autor do PR e o aprovador sao pessoas diferentes.

## Modo solo controlado

Se Gabriel for a unica pessoa que pode aprovar producao, existem duas opcoes praticas.

Nao existe um jeito limpo de "aprovar a si mesmo" com `Required approvals: 1`. Para projeto solo, escolha uma das opcoes abaixo.

Opcao 1, mais simples para projeto solo:

- Manter CI obrigatorio em `staging` e `main`.
- Remover `Required approvals: 1` das rulesets.
- Deixar somente Gabriel com permissao de merge.

Opcao 2, mais rigida:

- Manter `Required approvals: 1`.
- Adicionar Gabriel na `Bypass list` das rulesets de `staging` e `main`.
- Usar bypass apenas quando for uma mudanca propria e documentar no PR o motivo.

Nao use push direto em `main` como rotina, mesmo tendo permissao.

## Checklist rapido de release

Antes de `develop -> staging`:

- CI verde.
- Mudancas revisadas.
- Variaveis de ambiente conferidas.
- Migrations entendidas.
- Homologacao pronta.

Antes de `staging -> main`:

- Staging validado.
- CI verde.
- Dados e migrations conferidos.
- Producao pronta.
- Plano de rollback anotado.

## Comandos uteis

Atualizar `develop`:

```bash
git checkout develop
git pull origin develop
```

Criar branch de trabalho:

```bash
git checkout -b feature/nome-da-mudanca
```

Enviar branch:

```bash
git push -u origin feature/nome-da-mudanca
```

Ver branches locais:

```bash
git branch
```

Ver estado atual:

```bash
git status
```
