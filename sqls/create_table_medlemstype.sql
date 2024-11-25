CREATE TABLE Medlemstype (
    Id                  INTEGER     NOT NULL    PRIMARY KEY,
    Navn                TEXT        NOT NULL,
    AldersgruppeId      INTEGER     NOT NULL,
    FOREIGN KEY (AldersgruppeId) REFERENCES Aldersgruppe(Id)
);