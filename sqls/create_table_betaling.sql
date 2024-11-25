CREATE TABLE Betaling (
    Id                  INTEGER     NOT NULL    PRIMARY KEY,
    KontigentId         INTEGER     NOT NULL,
    MedlemsId           INTEGER     NOT NULL,
    BelopNOK            INTEGER     NOT NULL,
    InnbetaltDato      TEXT        NOT NULL,
    FOREIGN KEY (KontigentId) REFERENCES Kontigent(Id),
    FOREIGN KEY (MedlemsId) REFERENCES Medlem(Id)
);