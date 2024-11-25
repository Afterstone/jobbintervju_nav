import argparse
import typing as t
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

import sqlite_loader.db as db


@dataclass
class Args:
    path_db: Path
    path_medlemmer_csv: Path
    path_kontigent_csv: Path
    path_betalinger_csv: Path
    csv_separator: str

    def __post_init__(self):
        file_not_found_message = 'Fant ikke filen {}. Sjekk at filstien er riktig.'
        if not all((
            self.path_medlemmer_csv.exists(),
            self.path_kontigent_csv.exists(),
            self.path_betalinger_csv.exists(),
        )):
            raise FileNotFoundError(file_not_found_message.format(self.path_medlemmer_csv))


def parse_args():
    parser = argparse.ArgumentParser(description='Last medlemsdata inn i en sqlite-database')
    parser.add_argument('--filsti-database', type=str, help='Filstien der databasen vil bli lagret', default='./data/medlemsdata.db')

    parser.add_argument('--filsti-medlemmer', type=str, help='Filstien til medlemsdata', default='./data/Medlemmer.csv')
    parser.add_argument('--filsti-kontigent', type=str, help='Filstien til kontigentdata', default='./data/Kontingent.csv')
    parser.add_argument('--filsti-betalinger', type=str, help='Filstien til betalingsdata', default='./data/Betalinger.csv')

    parser.add_argument('--csv-separator', type=str, help='Separator for CSV-filene', default=';')

    args = parser.parse_args()

    args = Args(
        path_db=Path(args.filsti_database),
        path_medlemmer_csv=Path(args.filsti_medlemmer),
        path_kontigent_csv=Path(args.filsti_kontigent),
        path_betalinger_csv=Path(args.filsti_betalinger),
        csv_separator=args.csv_separator,
    )

    return args


def check_df_has_expected_column_names(df: pd.DataFrame, label: str, expected_columns: set[str]) -> None:
    if not expected_columns.issubset(df.columns):
        raise ValueError(f'{label}: Kolonnene {expected_columns - set(df.columns)} mangler, sjekk CSV-filen.')


def check_df_has_correct_data_types(df: pd.DataFrame, label: str, expected_dtypes: dict) -> None:
    for column, dtype in expected_dtypes.items():
        if df[column].dtype != dtype:
            raise ValueError(f'{label}: Kolonnen {column} har feil datatype, forventet {dtype}.')


def strip_trailing_whitespace(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    object_cols = df.select_dtypes(include='object').columns
    df[object_cols] = df[object_cols].apply(lambda x: x.str.strip())
    return df


def remove_empty_cols(df: pd.DataFrame) -> pd.DataFrame:
    return df.dropna(axis=1, how='all')


def check_df_has_nan_values(df: pd.DataFrame, label: str) -> None:
    nan_cols = df.columns[df.isna().any()].tolist()
    if nan_cols:
        nan_rows = df[df.isna().any(axis=1)]
        raise ValueError(f'{label}: Kolonner inneholder tomme verdier, sjekk CSV-filen.\n{nan_rows}')


def get_df_medlemmer(
    csv_path: Path,
    csv_separator: str = ';',
) -> pd.DataFrame:
    expected_dtypes: dict[str, str] = {
        'Medlemsnummer': 'int64',
        'Fornavn': 'object',
        'Etternavn': 'object',
        'Fødselsdato': 'object',
        'Kjønn': 'object',
        'Medlemstype': 'object',
        'Gateadresse': 'object',
        'Postnummer': 'object',
        'Poststed': 'object'
    }
    df_medlemmer = pd.read_csv(
        csv_path,
        sep=csv_separator,
        dtype={'Postnummer': 'object'}
    )
    check_df_has_expected_column_names(
        df=df_medlemmer,
        label=str(csv_path),
        expected_columns=set(expected_dtypes.keys()),
    )
    df_medlemmer = remove_empty_cols(df_medlemmer)
    check_df_has_correct_data_types(
        df=df_medlemmer,
        label=str(csv_path),
        expected_dtypes=expected_dtypes,
    )
    check_df_has_nan_values(df_medlemmer, str(csv_path))
    df_medlemmer = strip_trailing_whitespace(df_medlemmer)

    return df_medlemmer


def get_df_kontigent(csv_path: Path, csv_separator: str = ';') -> pd.DataFrame:
    expected_dtypes: dict[str, str] = {'Medlemstype': 'object', 'Kontingent': 'int64', 'Periode': 'int64', 'Aldersgruppe': 'object'}
    df_kontigent = pd.read_csv(csv_path, sep=csv_separator)
    check_df_has_expected_column_names(
        df=df_kontigent,
        label=str(csv_path),
        expected_columns=set(expected_dtypes.keys()),
    )
    df_kontigent = remove_empty_cols(df_kontigent)
    check_df_has_correct_data_types(
        df=df_kontigent,
        label=str(csv_path),
        expected_dtypes=expected_dtypes,
    )
    check_df_has_nan_values(df_kontigent, str(csv_path))
    df_kontigent = strip_trailing_whitespace(df_kontigent)

    return df_kontigent


def get_df_betalinger(csv_path: Path, csv_separator: str = ';') -> pd.DataFrame:
    expected_dtypes: dict[str, str] = {'Medlemsnummer': 'int64', 'Beløp': 'int64', 'Periode': 'int64', 'InnbetaltDato': 'object'}
    df_betalinger = pd.read_csv(csv_path, sep=csv_separator)
    check_df_has_expected_column_names(
        df=df_betalinger,
        label=str(csv_path),
        expected_columns=set(expected_dtypes.keys()),
    )
    df_betalinger = remove_empty_cols(df_betalinger)
    check_df_has_correct_data_types(
        df=df_betalinger,
        label=str(csv_path),
        expected_dtypes=expected_dtypes,
    )
    check_df_has_nan_values(df_betalinger, str(csv_path))
    df_betalinger = strip_trailing_whitespace(df_betalinger)

    return df_betalinger


def add_poststed(db_path: Path, postnummer: t.Sequence[int], poststed: t.Sequence[str]) -> None:
    error = False
    for p in postnummer:
        if len(str(p)) != 4:
            print(f'ADVARSEL: Postnummer {p} er ikke fire siffer. Sjekk CSV-filen.')
            error = True
    if error:
        raise ValueError('Et eller flere postnummer er ikke fire siffer. Fiks dette i CSV-filen.')

    tuples = list(set(zip(postnummer, poststed)))

    unique_check = defaultdict(list)
    for pn, ps in tuples:
        unique_check[pn].append(ps)

    error = False
    for pn, ps_list in unique_check.items():
        if len(ps_list) > 1:
            print(f'ADVARSEL: Postnummer {pn} har flere poststeder: {ps_list}')
            error = True
    if error:
        raise ValueError('Et eller flere postnummer har flere poststeder. Fiks dette i CSV-filen.')

    db.insert_into_table(
        db_path=db_path,
        table_name='Poststed',
        columns=['Postnummer', 'Navn'],
        values=tuples,
    )


def add_adresse(db_path: Path, gateadresse: t.Sequence[str], postnummer: t.Sequence[int]) -> None:
    db.insert_into_table(
        db_path=db_path,
        table_name='Adresse',
        columns=['Gateadresse', 'Postnummer'],
        values=list((g, p) for g, p in zip(gateadresse, postnummer)),
    )


def add_aldersgrupper(db_path: Path, aldersgrupper: t.Sequence[str]) -> None:
    db.insert_into_table(
        db_path=db_path,
        table_name='Aldersgruppe',
        columns=['Navn'],
        values=list((x.lower(),) for x in set(aldersgrupper)),
    )


def add_medlemstype(db_path: Path, medlemstyper: t.Sequence[str], aldersgrupper: t.Sequence[str]) -> None:
    aldersgruppe_rows = db.get_rows(db_path=db_path, table_name='Aldersgruppe', columns=['Id', 'Navn'])
    aldersgruppe_dict = {navn.lower(): id for id, navn in aldersgruppe_rows}

    tuples = []
    for m, a in zip(medlemstyper, aldersgrupper):
        tuples.append((m, aldersgruppe_dict[a.lower()]))

    db.insert_into_table(
        db_path=db_path,
        table_name='Medlemstype',
        columns=['Navn', 'AldersgruppeId'],
        values=tuples,
    )


def add_kjonn(db_path: Path, kjonn: t.Sequence[str]) -> None:
    db.insert_into_table(
        db_path=db_path,
        table_name='Kjonn',
        columns=['Kjonn'],
        values=list((x,) for x in set(kjonn)),
    )


def add_kontigent(db_path: Path, df: pd.DataFrame) -> None:
    df = df.copy()

    medlemstype_rows = db.get_rows(db_path=db_path, table_name='Medlemstype', columns=['Id', 'Navn'])
    medlemstype_dict = {navn: id for id, navn in medlemstype_rows}
    df['MedlemstypeId'] = df['Medlemstype'].map(medlemstype_dict)

    kontigent_tuples = df[['MedlemstypeId', 'Periode', 'Kontingent']].values.tolist()

    db.insert_into_table(
        db_path=db_path,
        table_name='Kontigent',
        columns=['MedlemstypeId', 'Periode', 'KontingentNOK'],
        values=kontigent_tuples,
    )


def add_betalinger(db_path: Path, df: pd.DataFrame) -> None:
    df = df.copy()

    kontigent_rows = db.get_rows(db_path=db_path, table_name='Kontigent', columns=['Id', 'MedlemstypeId', 'Periode'])
    kontigent_dict = {(medlemstype_id, periode): id for id, medlemstype_id, periode in kontigent_rows}
    medlem_rows = db.get_rows(db_path=db_path, table_name='Medlem', columns=['Id', 'MedlemstypeId'])
    medlem_dict = {id: medlemstype_id for id, medlemstype_id in medlem_rows}
    df['KontigentId'] = df.apply(lambda x: kontigent_dict[(medlem_dict[x['Medlemsnummer']], x['Periode'])], axis=1)
    df['InnbetaltDatoIso'] = pd.to_datetime(df['InnbetaltDato'], format='%d.%m.%Y').dt.strftime('%Y-%m-%d')

    betalinger_tuples = df[['KontigentId', 'Medlemsnummer', 'Beløp', 'InnbetaltDatoIso']].values.tolist()

    db.insert_into_table(
        db_path=db_path,
        table_name='Betaling',
        columns=['KontigentId', 'MedlemsId', 'BelopNOK', 'InnbetaltDato'],
        values=betalinger_tuples,
    )


def add_medlemmer(db_path: Path, df: pd.DataFrame, max_age: int = 120) -> None:
    df = df.copy()

    unique_id_check = df['Medlemsnummer'].value_counts()
    if unique_id_check.max() > 1:
        duplicates = [v for v, c in unique_id_check.items() if c > 1]
        raise ValueError(
            'Det er duplikate medlemsnummer i CSV-filen. Fiks dette før du laster inn dataen.'
            ' Aktuelle medlemsnummer: ' + ', '.join(map(str, duplicates))
        )

    df.rename(columns={'Medlemsnummer': 'Id'}, inplace=True)

    medlem_rows = db.get_rows(db_path=db_path, table_name='Kjonn', columns=['Id', 'Kjonn'])
    medlem_dict = {kjonn: id for id, kjonn in medlem_rows}
    df['KjonnId'] = df['Kjønn'].map(medlem_dict)

    medlemstype_rows = db.get_rows(db_path=db_path, table_name='Medlemstype', columns=['Id', 'Navn'])
    medlemstype_dict = {navn.lower(): id for id, navn in medlemstype_rows}
    df['MedlemstypeId'] = df['Medlemstype'].apply(lambda x: medlemstype_dict[x.lower()])

    adresse_rows = db.get_rows(db_path=db_path, table_name='Adresse', columns=['Id', 'Gateadresse', 'Postnummer'])
    adresse_dict = {(gateadresse, postnummer): id for id, gateadresse, postnummer in adresse_rows}
    df['AdresseId'] = df.apply(lambda x: adresse_dict[(x['Gateadresse'], str(x['Postnummer']))], axis=1)

    df['FødselsdatoIso'] = pd.to_datetime(df['Fødselsdato'], format='%d.%m.%Y').dt.strftime('%Y-%m-%d')

    df['Age'] = pd.to_datetime('today').year - pd.to_datetime(df['Fødselsdato'], format='%d.%m.%Y').dt.year
    if df['Age'].min() < 0:
        df_selected = df[df['Age'] < 0]
        print('ADVARSEL: Et eller flere medlemmer har en fødselsdato som er i fremtiden. Sjekk CSV-filen.')
        print(f"Medlemmer med fødselsdato i fremtiden:\n{df_selected[['Id', 'Fornavn', 'Etternavn', 'Fødselsdato']]}\n")
        raise ValueError('En eller flere medlemmer har en fødselsdato som er i fremtiden. Sjekk CSV-filen.')

    if df['Age'].max() > max_age:
        df_selected = df[df['Age'] > max_age]
        print(f'ADVARSEL: Et eller flere medlemmer har en alder over {max_age} år. Sjekk CSV-filen.')
        print(f"Medlemmer med alder over {max_age} år:\n{df_selected[['Id', 'Fornavn', 'Etternavn', 'Fødselsdato']]}\n")
        raise ValueError(f'Et eller flere medlemmer har en alder over {max_age} år. Sjekk CSV-filen.')

    medlem_tuples = df[['Id', 'Fornavn', 'Etternavn', 'FødselsdatoIso', 'KjonnId', 'MedlemstypeId', 'AdresseId']].values.tolist()

    db.insert_into_table(
        db_path=db_path,
        table_name='Medlem',
        columns=['Id', 'Fornavn', 'Etternavn', 'Fodselsdato', 'KjonnId', 'MedlemstypeId', 'AdresseId'],
        values=medlem_tuples,
    )


def main():
    args = parse_args()

    db.init_database(db_path=args.path_db, overwrite=True)

    df_medlemmer = get_df_medlemmer(csv_path=args.path_medlemmer_csv, csv_separator=args.csv_separator)
    df_kontigent = get_df_kontigent(csv_path=args.path_kontigent_csv, csv_separator=args.csv_separator)
    df_betalinger = get_df_betalinger(csv_path=args.path_betalinger_csv, csv_separator=args.csv_separator)

    print("Legger inn poststed...")
    add_poststed(db_path=args.path_db, postnummer=df_medlemmer['Postnummer'].tolist(), poststed=df_medlemmer['Poststed'].tolist())

    print("Legger inn adresse...")
    add_adresse(db_path=args.path_db, gateadresse=df_medlemmer['Gateadresse'].tolist(), postnummer=df_medlemmer['Postnummer'].tolist())

    print("Legger inn aldersgrupper...")
    add_aldersgrupper(db_path=args.path_db, aldersgrupper=df_kontigent['Aldersgruppe'].tolist())

    print("Legger inn medlemstype...")
    add_medlemstype(db_path=args.path_db, medlemstyper=df_kontigent['Medlemstype'].tolist(), aldersgrupper=df_kontigent['Aldersgruppe'].tolist())

    print("Legger inn kjønn...")
    add_kjonn(db_path=args.path_db, kjonn=df_medlemmer['Kjønn'].tolist())

    print("Legger inn kontigent...")
    add_kontigent(db_path=args.path_db, df=df_kontigent)

    print("Legger inn medlemmer...")
    add_medlemmer(db_path=args.path_db, df=df_medlemmer)

    print("Legger inn betalinger...")
    add_betalinger(db_path=args.path_db, df=df_betalinger)

    print()
    print('Alt er lastet inn i databasen.')


if __name__ == '__main__':
    main()
