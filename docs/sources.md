# Registro de fontes

Tabela de todas as fontes de dados consideradas: origem, o que entregam, sob quais termos e quando foram verificadas. Regra: **nenhuma fonte entra no pipeline antes de ficar `aprovada`** (ver [ADR 0001](adr/0001-fontes-hibridas-de-dados.md)).

Status possíveis: `pendente` (termos ainda não conferidos), `aprovada`, `descartada`, `não avaliada`.

Última verificação: 2026-09-28.

| Fonte | O que fornece | Acesso | Termos e licença | Uso previsto | Status |
| --- | --- | --- | --- | --- | --- |
| [football-data.org](https://www.football-data.org) (API) | Série A: resultados, agenda e tabela | Plano gratuito: 10 chamadas por minuto, placares com atraso. Histórico de 10 temporadas só em plano pago | Política de uso da API ainda não lida | Temporada corrente | `pendente` |
| [football-data.co.uk](https://football-data.co.uk/brazil.php) (CSV) | Resultados históricos e odds do Brasil (arquivo `new/BRA.csv`, atualizado em 22/09/26 segundo o site) | Download gratuito | Aviso legal e `notes.txt` não lidos (o site bloqueou a leitura em 2026-09-28) | Histórico em massa | `pendente` |
| Kaggle: Brazilian Soccer Odds Data (endereço exato a confirmar) | Odds de todas as partidas do Brasileirão, 2012 a 2024 | Download | MIT declarada no Kaggle, mas a base parte do football-data.co.uk com dados raspados do oddsportal; a origem dos dados subjacentes precisa de checagem | Candidata a Benchmark de mercado | `pendente` |
| API-Football | Dados de partidas de muitas ligas | Plano gratuito de 100 requisições por dia (segundo comparações de terceiros) | Não lidos | Complementar, se necessário | `não avaliada` |

## Como atualizar

Ao adicionar ou revisar uma fonte, preencha todas as colunas, atualize a data de última verificação e, se a decisão for difícil de reverter, registre um ADR.
