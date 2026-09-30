# Futebol

Projeto de aprendizado hands-on em ciência de dados aplicada ao futebol: coletar dados de APIs públicas gratuitas, estudar a teoria por trás dos modelos, treinar abordagens estatísticas e de ML e fechar o ciclo com deploy e monitoração, tudo a custo zero.

## Language

### Escopo

**Time-foco**:
O Vasco da Gama, clube sobre o qual recaem as previsões, os painéis e os exemplos do projeto.
_Avoid_: time do coração, time principal

**Universo de treino**:
Conjunto das partidas de todos os times da Série A do Campeonato Brasileiro, usado para ajustar os modelos. A Série B fica de fora.
_Avoid_: base de dados, dataset

### Previsão

**Alvo**:
As probabilidades de vitória, empate e derrota do Time-foco na próxima partida do Campeonato Brasileiro.
_Avoid_: previsão, palpite, resultado previsto

**Escada de modelos**:
Sequência de abordagens (rating Elo, Poisson e Dixon-Coles, gradient boosting) que respondem ao mesmo Alvo e são comparadas com as mesmas métricas.
_Avoid_: modelo final, ranking de modelos

**xG (gols esperados)**:
Probabilidade de um chute virar gol, dada a qualidade da chance. Fica fora da primeira versão da Escada de modelos; é extensão opcional se houver dados de chutes gratuitos e legítimos.
_Avoid_: qualidade de chute

**Clube promovido**:
Clube que entra na Série A sem histórico recente na divisão; começa com um rating inicial abaixo da média (prior), regra explícita e documentada.
_Avoid_: novato, time estreante

**Benchmark de mercado**:
Odds de casas de apostas usadas só para comparar com os modelos ao final, nunca como feature de entrada.
_Avoid_: baseline de odds, feature de mercado

### Método

**Baseline**:
Previsão ingênua de referência para o Alvo: a frequência histórica de vitória, empate e derrota. Todo modelo da Escada de modelos precisa superá-la.
_Avoid_: modelo base, referência

**Checkpoint de teoria**:
Notebook que encerra cada fase e explica o modelo estudado: o que assume, onde falha e como se saiu na Escada de modelos. É o ponto de pausa natural do projeto.
_Avoid_: resumo, retrospectiva

### Dados

**Registro de fontes**:
Tabela versionada no repositório com origem, licença e data de coleta de cada fonte de dados usada.
_Avoid_: inventário de dados, lista de APIs

### Entrega

**Ciclo completo**:
Critério de "pronto": do dado bruto à previsão publicada e monitorada, ainda que simples.
_Avoid_: MVP, versão final

**Custo zero**:
Regra de que nenhum serviço usado tem cobrança nem cartão de crédito cadastrado; se restringir deploy e monitoração, esses temas são tratados à parte.
_Avoid_: gratuito, barato
