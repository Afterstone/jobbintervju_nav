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