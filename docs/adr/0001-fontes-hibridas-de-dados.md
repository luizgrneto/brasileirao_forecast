---
status: proposed
---

# Fontes de dados híbridas: histórico aberto + API oficial para a temporada corrente

O plano gratuito do football-data.org cobre a Série A brasileira, mas não inclui histórico de várias temporadas, que só vem em plano pago; isso não basta para treinar modelos e violaria o Custo zero. Decidimos combinar histórico em massa de dados abertos (CSV do football-data.co.uk, termos ainda a confirmar) com a API oficial para manter a temporada corrente atualizada, registrando origem, licença e data de coleta de cada fonte no Registro de fontes.

## Considered Options

- **Pagar por histórico:** descartado pela regra de Custo zero.
- **Raspar sites que exibem os dados:** descartado por fragilidade e risco com termos de uso.

## Consequences

- Fontes distintas exigem reconciliar nomes e identificadores de clubes.
- Nenhuma fonte entra no pipeline antes de a licença e os termos de uso serem conferidos e anotados no Registro de fontes (`docs/sources.md`).
