import sqlite3

connection = sqlite3.connect('weinkeller.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

# Beispielweine einfügen
cur.execute("""INSERT INTO weine 
    (name, jahrgang, weingut, rebsorte, region, lagerposition, trinktemperatur, preis, notizen) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
    ('Château Margaux', 2015, 'Château Margaux', 'Cabernet Sauvignon', 
     'Bordeaux', 'Regal A, Fach 3', '16-18°C', 950.00, 
     'Exzellenter Jahrgang mit langem Lagerpotential')
)

cur.execute("""INSERT INTO weine 
    (name, jahrgang, weingut, rebsorte, region, lagerposition, trinktemperatur, preis, notizen) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
    ('Moselriesling Auslese', 2018, 'Weingut Dr. Loosen', 'Riesling', 
     'Mosel', 'Regal B, Fach 1', '8-10°C', 42.50, 
     'Fruchtig mit feiner Säure')
)

connection.commit()
connection.close()

