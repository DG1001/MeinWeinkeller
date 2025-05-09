DROP TABLE IF EXISTS weine;

CREATE TABLE weine (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    jahrgang INTEGER NOT NULL,
    weingut TEXT NOT NULL,
    rebsorte TEXT NOT NULL,
    region TEXT,
    lagerposition TEXT,
    trinktemperatur TEXT,
    kaufdatum DATE,
    preis FLOAT,
    bewertung INTEGER,
    notizen TEXT,
    bestand INTEGER DEFAULT 1,
    bild_pfade TEXT, -- Comma-separated list of image filenames
    ai_beschreibung TEXT, -- AI-generated markdown description
    erstellt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    aktualisiert TIMESTAMP
);

