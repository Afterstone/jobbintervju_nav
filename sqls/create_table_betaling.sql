CREATE TABLE Betaling (
    Id                  INTEGER     NOT NULL    PRIMARY KEY,
    KontingentId         INTEGER     NOT NULL,
    MedlemsId           INTEGER     NOT NULL,
    BelopNOK            INTEGER     NOT NULL,
    InnbetaltDato      TEXT        NOT NULL,
    FOREIGN KEY (KontingentId) REFERENCES Kontingent(Id),
    FOREIGN KEY (MedlemsId) REFERENCES Medlem(Id)
);