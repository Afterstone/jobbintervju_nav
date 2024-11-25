CREATE TABLE Adresse (
    Id                  INTEGER     NOT NULL    PRIMARY KEY,
    Postnummer          TEXT        NOT NULL,
    Gateadresse         TEXT        NOT NULL,
    FOREIGN KEY (Postnummer) REFERENCES Poststed(Postnummer)
);