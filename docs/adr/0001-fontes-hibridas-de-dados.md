---
status: accepted
---

# Fontes de dados híbridas: histórico aberto + API oficial para a temporada corrente

O plano gratuito do football-data.org cobre a Série A brasileira, mas não inclui histórico de várias temporadas, que só vem em plano pago; isso não basta para treinar modelos e violaria o Custo zero. Decidimos combinar histórico em massa de dados abertos (CSV do football-data.co.uk, termos ainda a confirmar) com a API oficial para manter a temporada corrente atualizada, registrando origem, licença e data de coleta de cada fonte no Registro de fontes.

## Considered Options

- **Pagar por histórico:** descartado pela regra de Custo zero.
- **Raspar sites que exibem os dados:** descartado por fragilidade e risco com termos de uso.

## Consequences

- Fontes distintas exigem reconciliar nomes e identificadores de clubes.
- Nenhuma fonte entra no pipeline antes de a licença e os termos de uso serem conferidos e anotados no Registro de fontes (`docs/sources.md`).
- O football-data.co.uk limita o uso gratuito a pessoas físicas e rejeita bots, scrapers e produtos de treino de dados com IA (conferido em 2026-10-01). Decidimos aceitar o risco e usar o CSV, entendendo o projeto como uso pessoal e educativo, sem fins comerciais. Mitigações: o download é feito à mão, os dados brutos nunca vão para o git, a fonte é citada e a decisão é revista se o projeto ganhar fins comerciais ou se o autor da fonte se opuser. A rotina agendada da Fase 4 não baixa o CSV; como ela obtém o histórico fica para a Fase 4.
