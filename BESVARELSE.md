# Oppgave 2.gangsintervju Nav IT

Som nevnt ønsker vi at du skal presentere din løsning på en oppgave i intervjuet vi skal ha for stilling som dataplattformingeniør / utvikler hos oss i Nav IT, se beskrivelse nedenfor. Vi estimerer forberedelsestid til å være to-tre timer. Ikke nøl med å ta kontakt om noe er uklart!

## Bakgrunn:
Vedlagt er tre filer med data fra et medlemsregister for en fiktiv klubb. Filene inneholder data om medlemmer, kontingent og betalinger.

Økonomiansvarlig i klubben er lei av mye manuelt arbeid med data fra flere filer som oppstår hver gang han må lage rapporter over medlemmer og deres medlemskap. Han ber deg om å lage en database med alle dataene, slik at han fort kan kjøre SQL-spørringer når han trenger data. Du står fritt til å velge datastruktur.

### Svar:

Jeg har valgt å tenke litt rundt denne oppgaven før jeg starter på selve Python-koden. Det er flere feil man kan avdekke ved å grunnleggende på visualisert innhold og f.eks. på unike kolonneverdier.

Ideelt skulle man ønske nærmere kontakt med relevante interessenter i et slikt prosjekt, for å kunne avklare de eventuelle feilene og misforståelsene som dukker opp, samt avklare akseptansekriterier er.

Noen relevante spørsmål blir jo da:
- Et dette en one-off eller noe som skal kjøres jevnlig?
- Hvordan genereres dataene?
  - Excel/Google Sheets?
  - For hånd?
- Hvilke tegnsett brukes?
- Bør brukeren heller bruke Excel eller Google Sheets?
  - Datavask
  - Rapportering
  - Alternativ til SQL
- Hvordan skal dataene brukes videre?
- Videreutvikling og potensiale
- Vedlikehold?
- Hva bør fikses manuelt vs. i kode?
  - Iterativ prosess?
- Er dette et prosjekt som kan leve over lengre tid uten mye tilsyn?
  - F.eks. om vi hjelper dem pro bono som venner av klubben vs. om vi er ansatt/kan fakturere for dette.
- Hvordan oppdager man om det er feil i dataene?
  - Tanker om type feil.
- Hvor lett er det å få inn andre å sette seg inn i systemet?
  - Valg av teknologi er relevant, f.eks. forksjell mellom Pythons CSV-bibliotek og sqlite3 vs. Pandas og SQLAlchemy.
- Hva er hensiktsmessig mtp. UX?
  - Skal bruker av systemet installere Python selv og kjøre scriptet på lokale filer? Integrere med f.eks. Google Drive? Opplasting via webgrensesnitt?
  - Må se an brukerens tekniske kompetanse og behov, sett opp mot vedlikeholdskostnader, kompleksitet og annet.

Begynner derfor med de enkleste oppgavene, som er å definere GitHub og GitHub Actions workflows, samt prosjektstruktur.
- Har valgt uv som verktøy for pakkeinstallasjon og virtuelle miljøer grunnet utelse vs. venv/virtualenv.
- Har satt opp den etterspurte workflowen for linting av Python-kode, hvor jeg har valgt å teste både flake8 og pylint.



## Din hjemmeoppgave:

- Koden må publiseres i eget repo på Github.
  - Koden er satt opp i repoet [Afterstone/jobbintervju_nav](https://github.com/Afterstone/jobbintervju_nav/).
- Github repoet må ha en workflow som trigges av nye committer og sjekker om Python-kode har riktig syntaks.
  - Dette er satt opp med flake8 som linter.
    - [Link til workflow-fil](https://github.com/Afterstone/jobbintervju_nav/blob/main/.github/workflows/linting.yaml).
    - [Link til workflow runs](https://github.com/Afterstone/jobbintervju_nav/actions/workflows/linting.yaml).
- Lag et program i Python som importerer data fra de tre angitte filene til en SQLite database. Programmet må tåle at det kan være litt dårlig kvalitet på dataene i filene, de ble jo laget for hånd.

### Analyse

Går så videre til å analysere dataene. I fila [notebooks/overview.ipynb](notebooks/overview.ipynb) ligger en gjennomgang av CSV-filene. Det mest relevante er:
- Forskjell i hvor konsekvente filnavnene er.
- Flere kolonnenavn har mellomrom i seg.
- Betalinger
  - Noen verdier kan ses på som outliers, ref. Periode og Innbetalt_dato.
- Kontigent
  - Flere kolonner har mellomrom i verdiene.
  - Et kolonnenavn har liten forbokstav.
- Medlemmer
  - To tomme kolonner
  - Etternavn har nullverdier
  - Etternavn har store bokstaver, usikker på om det er et problem.
  - Medlemstype varierer mellom liten/stor forbokstav.
  - Postnummer med 3 siffer.
  - Gateadresse har mellomrom foran eller bak.

Basert på analysen virker det som at det er en del feil i dataene. Flere av disse problemene kan vi gå frem med ved å kjøre "fiks først, spør etterpå". I utgangspunktet er dette en iterativ prosess, men vi har både begrenset med tid og tilgang på kunden.

### Implementasjon av programmet

Har satt opp forslag til ER-diagram og datatyper i [diagrams/database.md](diagrams/database.md).

## Besvar følgende spørsmål:
- Hvordan strukturerte du data i databasen?
  - Har satt opp forslag til ER-diagram og datatyper i [diagrams/database.md](diagrams/database.md).
- Hva kan være viktig å passe på ved innlesing av data?
- Hva tenker du om valg av datamodell?
  - Det er flere måter å gjøre dette på.
  - Kompleksitet i tråd med bruker.
  - Muligheter for utvidelse.
  - Sqlite har fleksible datatyper.
  - Kolonnevalg
    - Periode - årstall (text/int) vs. start+sluttdato (text)
    - Adresse
      - Postnummer - int vs. text
    - 
- Hvilke SQL-spørringer kan man kjøre mot databasen for å sjekke om medlemmet med medlemsnummer 57 har betalt riktig kontingent?
  
```sql
SELECT
    M.id AS MedlemsId,
    M.Fornavn,
    M.Etternavn,
    M.Fodselsdato,
    (DATE('now') - M.Fodselsdato) AS Alder,
    AG.Navn AS Aldersgruppe,
    CASE
      WHEN AG.Navn = '10-17' THEN CASE WHEN (DATE('now') - M.Fodselsdato) >= 10 AND (DATE('now') - M.Fodselsdato) < 17 THEN true ELSE false END
      WHEN AG.Navn = '18-60' THEN CASE WHEN (DATE('now') - M.Fodselsdato) >= 18 AND (DATE('now') - M.Fodselsdato) < 60 THEN true ELSE false END
      WHEN AG.Navn = '60 +' THEN CASE WHEN (DATE('now') - M.Fodselsdato) >= 60 THEN true ELSE false END
      ELSE false
    END AS KontigentGyldig
FROM
  Medlem AS M
  LEFT JOIN Betaling AS B ON M.id = B.MedlemsId
  LEFT JOIN Kontigent AS K ON K.Id = B.KontigentId
  LEFT JOIN Medlemstype AS MT ON MT.Id = m.MedlemstypeId
  LEFT JOIN Aldersgruppe AS AG ON AG.Id = MT.AldersgruppeId
WHERE
  -- M.id = 57
  KontigentGyldig = false
;
```

I intervjuet ønsker vi at du presenterer ditt svar på oppgaven og gjør en demo av Python programmet. Du velger selv presentasjonsform, og du har 15 minutter til rådighet.
