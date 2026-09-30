# Convenções

## Idioma

- Documentação didática (`docs/`, notebooks, `CONTEXT.md`): português brasileiro, mantendo em inglês os termos técnicos consagrados (xG, Elo, RPS).
- Código, nomes de variáveis, mensagens de commit e o README de apresentação: inglês.

## Commits

- Mensagens em inglês, no imperativo, explicando o porquê quando não for óbvio: `add Elo rating with home advantage`.
- Commits pequenos, um por peça lógica.

## Notebooks

- Versionados sem saídas. Rode `make hooks` uma vez para isso acontecer automaticamente no commit.
- Cada fase termina com um Checkpoint de teoria, baseado em [`checkpoint-template.md`](checkpoint-template.md).

## Documentos de decisão

- `CONTEXT.md` é só glossário: define termos, sem detalhes de implementação.
- Um ADR só é escrito quando a decisão é difícil de reverter, surpreendente sem contexto e resultado de um trade-off real.

## Dados

- Nada de dados brutos no git. Toda fonte precisa estar no [Registro de fontes](sources.md) com status `aprovada` antes de entrar no pipeline.
