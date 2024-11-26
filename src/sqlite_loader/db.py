import sqlite3
from pathlib import Path

from sqlite_loader.config import SQLS_FOLDER_PATH


def _create_table_poststed(c: sqlite3.Cursor):
    c.execute((SQLS_FOLDER_PATH / 'create_table_poststed.sql').read_text())


def _create_table_adresse(c: sqlite3.Cursor):
    c.execute((SQLS_FOLDER_PATH / 'create_table_adresse.sql').read_text())


def _create_table_aldergruppe(c: sqlite3.Cursor):
    c.execute((SQLS_FOLDER_PATH / 'create_table_aldergruppe.sql').read_text())


def _create_table_medlemstype(c: sqlite3.Cursor):
    c.execute((SQLS_FOLDER_PATH / 'create_table_medlemstype.sql').read_text())


def _create_table_kjonn(c: sqlite3.Cursor):
    c.execute((SQLS_FOLDER_PATH / 'create_table_kjonn.sql').read_text())


def _create_table_kontingent(c: sqlite3.Cursor):
    c.execute((SQLS_FOLDER_PATH / 'create_table_kontingent.sql').read_text())


def _create_table_medlem(c: sqlite3.Cursor):
    c.execute((SQLS_FOLDER_PATH / 'create_table_medlem.sql').read_text())


def _create_table_betaling(c: sqlite3.Cursor):
    c.execute((SQLS_FOLDER_PATH / 'create_table_betaling.sql').read_text())


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
            _create_table_adresse(c)
            _create_table_poststed(c)
            _create_table_aldergruppe(c)
            _create_table_medlemstype(c)
            _create_table_kjonn(c)
            _create_table_kontingent(c)
            _create_table_medlem(c)
            _create_table_betaling(c)
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
