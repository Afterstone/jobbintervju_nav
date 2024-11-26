CREATE TABLE Kontingent (
    Id                  INTEGER     NOT NULL    PRIMARY KEY,
    MedlemstypeId       INTEGER     NOT NULL,
    Periode             INTEGER     NOT NULL,
    KontingentNOK       INTEGER     NOT NULL,
    FOREIGN KEY (MedlemstypeId) REFERENCES Medlemstype(Id)
);