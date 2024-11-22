# Jobbintervju NAV

## Intro

Dette prosjektet er en oppgave i forbindelse med et jobbintervju hos NAV IT Høsten 2024. Oppgaveteksten er tilgjengelig via [OPPGAVE.md](OPPGAVE.md).

## Oppsett

### Installasjon

Prosjektet er satt opp med uv som Python pakkebehandler. For å installere uv, se instruksjoner [her](https://docs.astral.sh/uv/guides/install-python/).

Deretter kan prosjektets avhengigheter installeres med:

```bash
# Kjør alternativt 'uv sync' for å lage et virtuelt Python-miljø.
uv sync
```

## Bruk (WiP)

## Verktøyer

### Github Actions

For å kjøre workflows lokalt anbefales det å bruke [Act](https://github.com/nektos/act). Dette kan [installeres som en extension i Github actions CLI-verktøyet](https://nektosact.com/installation/gh.html).

### Linting

Linting kan gjøres via flake8:

```bash
uvx flake8 src/ tests/
```

Flake8 bruker konfigurasjonsdetaljer fra `setup.cfg`.

## Testing (WiP)

## Notebooks (WiP)
