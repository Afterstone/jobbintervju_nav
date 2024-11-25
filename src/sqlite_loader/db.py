import sqlite3
from pathlib import Path


def create_table_poststed(c: sqlite3.Cursor):
    c.execute('''
        CREATE TABLE Poststed (
            Postnummer          TEXT        NOT NULL    PRIMARY KEY,
            Navn                TEXT
        );
    ''')


def create_table_adresse(c: sqlite3.Cursor):
    c.execute('''
        CREATE TABLE Adresse (
            Id                  INTEGER     NOT NULL    PRIMARY KEY,
            Postnummer          TEXT        NOT NULL,
            Gateadresse         TEXT        NOT NULL,
            FOREIGN KEY (Postnummer) REFERENCES Poststed(Postnummer)
        );
    ''')


def create_table_aldergruppe(c: sqlite3.Cursor):
    c.execute('''
        CREATE TABLE Aldersgruppe (
            Id                  INTEGER     NOT NULL    PRIMARY KEY,
            Navn                TEXT        NOT NULL    UNIQUE
        );
    ''')


def create_table_medlemstype(c: sqlite3.Cursor):
    c.execute('''
        CREATE TABLE Medlemstype (
            Id                  INTEGER     NOT NULL    PRIMARY KEY,
            Navn                TEXT        NOT NULL,
            AldersgruppeId      INTEGER     NOT NULL,
            FOREIGN KEY (AldersgruppeId) REFERENCES Aldersgruppe(Id)
        );
    ''')


def create_table_kjonn(c: sqlite3.Cursor):
    c.execute('''
        CREATE TABLE Kjonn (
            Id                  INTEGER     NOT NULL    PRIMARY KEY,
            Kjonn               TEXT        NOT NULL    UNIQUE
        );
    ''')


def create_table_kontigent(c: sqlite3.Cursor):
    c.execute('''
        CREATE TABLE Kontigent (
            Id                  INTEGER     NOT NULL    PRIMARY KEY,
            MedlemstypeId       INTEGER     NOT NULL,
            Periode             INTEGER     NOT NULL,
            KontingentNOK       INTEGER     NOT NULL,
            FOREIGN KEY (MedlemstypeId) REFERENCES Medlemstype(Id)
        );
        ''')


def create_table_medlem(c: sqlite3.Cursor):
    c.execute('''
        CREATE TABLE Medlem (
            Id                  INTEGER     NOT NULL    PRIMARY KEY,
            Fornavn             TEXT        NOT NULL,
            Etternavn           TEXT        NOT NULL,
            Fodselsdato         TEXT        NOT NULL,
            KjonnId             INTEGER     NOT NULL,
            MedlemstypeId       INTEGER     NOT NULL,
            AdresseId           INTEGER     NOT NULL,
            FOREIGN KEY (KjonnId) REFERENCES Kjonn(Id),
            FOREIGN KEY (MedlemstypeId) REFERENCES Medlemstype(Id),
            FOREIGN KEY (AdresseId) REFERENCES Adresse(Id)
        );
        ''')


def create_table_betaling(c: sqlite3.Cursor):
    c.execute('''
        CREATE TABLE Betaling (
            Id                  INTEGER     NOT NULL    PRIMARY KEY,
            KontigentId         INTEGER     NOT NULL,
            MedlemsId           INTEGER     NOT NULL,
            BelopNOK            INTEGER     NOT NULL,
            InnbetaltDato      TEXT        NOT NULL,
            FOREIGN KEY (KontigentId) REFERENCES Kontigent(Id),
            FOREIGN KEY (MedlemsId) REFERENCES Medlem(Id)
        );
    ''')


def init_database(db_path: Path, overwrite: bool = False):
    if db_path.exists():
        if overwrite:
            if db_path.is_dir():
                raise IsADirectoryError(f'{db_path} er en mappe. Slett mappen eller velg en annen filsti.')
            db_path.unlink()
        else:
            raise FileExistsError(f'Databasen {db_path} eksisterer allerede. Bruk --overskriv-database for å overskrive den.')
    with sqlite3.connect(db_path) as conn:
        conn.isolation_level = None
        c = conn.cursor()
        c.execute('begin')
        try:
            create_table_adresse(c)
            create_table_poststed(c)
            create_table_aldergruppe(c)
            create_table_medlemstype(c)
            create_table_kjonn(c)
            create_table_kontigent(c)
            create_table_medlem(c)
            create_table_betaling(c)
            c.execute('commit')
        except sqlite3.Error as e:
            print("Kunne ikke opprette tabellene, ruller tilbake endringer.")
            c.execute('rollback')
            raise e


def insert_into_table(db_path: Path, table_name: str, columns: list[str], values: list[tuple]):
    if isinstance(columns, list) is False:
        raise TypeError('columns må være en liste av strenger. Passerte du en enkelt streng?')

    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        try:
            c.execute('begin')
            c.executemany(f'INSERT INTO {table_name} ({", ".join(columns)}) VALUES ({", ".join(["?"] * len(columns))})', values)
            c.execute('commit')
        except sqlite3.Error as e:
            print(f"Kunne ikke legge til data i tabellen {table_name}, ruller tilbake endringer.")
            c.execute('rollback')
            raise e


def get_rows(
    db_path: Path,
    table_name: str,
    columns: list[str],
) -> list[tuple]:
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute(f'SELECT {", ".join(columns)} FROM {table_name}')
        return c.fetchall()
