# Roadmap

O projeto avança em fases. Cada fase termina com um **Checkpoint de teoria** (use o [modelo](checkpoint-template.md)), que é também a pausa natural para absorver o conteúdo antes de seguir. Termos em maiúscula inicial estão definidos em [`CONTEXT.md`](../CONTEXT.md).

Regras que valem para todas as fases:

- O **Alvo** é sempre o mesmo: probabilidades de vitória, empate e derrota do Vasco na próxima partida da Série A.
- Validação walk-forward: treina-se no passado e testa-se no futuro, sem embaralhar partidas.
- Métrica primária: RPS. Secundárias: log-loss e Brier score. Todo modelo é comparado com o **Baseline**.
- As odds das casas de apostas nunca entram como feature (ver **Benchmark de mercado**).
- **Custo zero**: nenhum serviço com cobrança ou cartão cadastrado.

## Fase 0: dados e baseline

- Coleta do histórico (CSV) e da temporada corrente (API), conforme o [Registro de fontes](sources.md).
- Mapa único de nomes de clubes entre as fontes.
- Registro de fontes v1, com licenças conferidas.
- Notebook exploratório que calcula o Baseline e o primeiro RPS de referência.
- Checkpoint: o que é o RPS, por que o Baseline importa e por que a validação é walk-forward.

## Fase 1: rating Elo

- Rating Elo com vantagem de mando e conversão do rating em probabilidades de vitória, empate e derrota.
- Regra explícita para **Clubes promovidos** (rating inicial abaixo da média).
- Checkpoint: suposições do Elo, sensibilidade ao fator K e calibração das probabilidades.

## Fase 2: Poisson e Dixon-Coles

- Modelo de gols com força de ataque e defesa por clube.
- Correção de placares baixos e decaimento temporal dos jogos antigos (Dixon-Coles).
- Checkpoint: a hipótese de gols como Poisson, onde ela falha e como o modelo se compara ao Elo.

## Fase 3: gradient boosting

- Features de forma recente, descanso e mando, sempre calculadas só com informação anterior à partida.
- Comparação da **Escada de modelos** inteira e, por fim, com o **Benchmark de mercado**.
- Opcional: **xG**, se surgirem dados de chutes gratuitos e legítimos.
- Checkpoint: risco de vazamento de informação, interpretabilidade e o que o boosting aprendeu a mais.

## Fase 4: deploy e monitoração

- Página estática com as probabilidades do próximo jogo do Vasco, atualizada a cada rodada por rotina agendada (GitHub Actions).
- Reajuste dos modelos após cada rodada, em modo walk-forward.
- Monitoração: RPS acumulado contra o Baseline e curva de calibração da temporada; a rotina abre um issue se o RPS dos últimos jogos ficar pior que o Baseline.
- Se o Vasco for rebaixado, as previsões sobre ele pausam e o treino continua na Série A.
- Checkpoint: como monitorar um modelo probabilístico e o que significa degradação nesse contexto.
