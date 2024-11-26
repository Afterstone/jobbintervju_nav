# Jobbintervju NAV

## Intro

Dette prosjektet er en oppgave i forbindelse med et jobbintervju hos NAV IT Høsten 2024. Oppgaveteksten er tilgjengelig via [OPPGAVE.md](OPPGAVE.md).

## Oppsett

### Installasjon

Prosjektet er satt opp med uv som Python pakkebehandler. For å installere uv, se instruksjoner [her](https://docs.astral.sh/uv/guides/install-python/).

Deretter kan prosjektets avhengigheter installeres med:

```bash
uv sync --no-dev
```

## Bruk

For å laste data fra CSV-filene til en SQLite database, legg dem i en mappe kalt `data/` i prosjektets rot. Man kan deretter kjøre følgende kommdo:

```bash
uv run python -m sqlite_loader.main \
    --filsti-medlemmer "data/Medlemmer.csv" \
    --filsti-kontigent "data/Kontingent.csv" \
    --filsti-betalinger "data/Betalinger.csv" \
    --filsti-database "data/Medlemsdata.db"
```

Man kan naturligvis bytte ut filstiene, om dette er ønskelig.

## Utvikling

### Installasjon

For å installere med utviklingsavhengigheter, kjør:

```bash
uv sync --extra dev
```

### Github Actions

For å kjøre workflows lokalt anbefales det å bruke [Act](https://github.com/nektos/act). Dette kan [installeres som en extension i Github actions CLI-verktøyet](https://nektosact.com/installation/gh.html).

### Linting

Linting kan gjøres via flake8:

```bash
uvx flake8 src/ tests/
```

Flake8 bruker konfigurasjonsdetaljer fra `setup.cfg`.

### Notebooks (WiP)

Notebooks for analyse av dataene ligger i `notebooks/`. Disse kan kjøres med Jupyter Notebook eller Jupyter Lab, men anses som out of scope for oppgaven.

### Testing (WiP)

Droppet i oppgaven grunnet tid.
