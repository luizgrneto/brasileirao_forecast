# brasileirao_forecast

Probabilistic match forecasts for the Brazilian Série A, with Vasco da Gama as the focus team.

**Status:** Phase 0 (data and baseline). The design is settled; the code is on its way.

## What this is

A hands-on learning project in applied football data science. It climbs a ladder of models, from a plain Elo rating to Poisson/Dixon-Coles to gradient boosting, and every rung answers the same question: *what are the win/draw/loss probabilities of Vasco da Gama's next Série A match?*

- **Same target, same yardstick.** Models are scored with walk-forward validation. The primary metric is the Ranked Probability Score (RPS); log-loss and Brier score are secondary. Each model must beat a naive baseline (historical outcome frequencies).
- **Bookmaker odds are a benchmark, never a feature.** They are used only at the end, to see how close the models get to the market.
- **Zero cost.** Free data sources, a local stack (Python, Parquet, DuckDB, MLflow) and a free scheduled workflow that publishes the forecasts as a static page.

## Sobre o projeto (pt-BR)

Este repositório é o diário de aprendizado de um projeto de ciência de dados aplicada ao futebol. A documentação didática está em português; código, nomes e commits estão em inglês. O treino usa toda a Série A do Campeonato Brasileiro e o Vasco da Gama é a lente: as previsões, os painéis e os exemplos são sobre ele.

Cada fase termina com um **Checkpoint de teoria**: um notebook que explica o modelo, o que ele assume, onde falha e como se saiu. É o ponto de pausa natural para absorver a teoria.

| Fase | Tema | Notebooks |
| --- | --- | --- |
| 0 | Dados e baseline | `notebooks/00_data_and_baseline/` |
| 1 | Rating Elo | `notebooks/01_elo/` |
| 2 | Poisson e Dixon-Coles | `notebooks/02_poisson_dixon_coles/` |
| 3 | Gradient boosting | `notebooks/03_gradient_boosting/` |
| 4 | Deploy e monitoração | `notebooks/04_deploy_and_monitoring/` |

Detalhes de cada fase: [`docs/roadmap.md`](docs/roadmap.md).

## Getting started

Requires [uv](https://docs.astral.sh/uv/) and Git.

```bash
git clone https://github.com/<your-user>/brasileirao_forecast.git
cd brasileirao_forecast
make setup   # install dependencies
make hooks   # strip notebook outputs on commit (run once)
make check   # lint + tests, same as CI
```

Run `make help` to list every command.

## Repository layout

```text
.
├── CONTEXT.md            # glossary of project terms (pt-BR)
├── docs/
│   ├── adr/              # architecture decision records
│   ├── roadmap.md        # phases and deliverables
│   ├── sources.md        # data source registry (origin, license, collection date)
│   ├── conventions.md    # language, commits, notebooks
│   └── checkpoint-template.md
├── notebooks/            # one folder per phase, each ending in a theory checkpoint
├── src/brasileirao_forecast/
├── tests/
└── data/                 # never versioned (see data/README.md)
```

## Data

Raw data is not committed. Where each source comes from, under which terms and when it was collected is tracked in [`docs/sources.md`](docs/sources.md). No source enters the pipeline before its terms are checked.

## License

Code is released under the [MIT License](LICENSE). Data sources keep their own terms.
