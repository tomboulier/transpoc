import sqlite3
from pathlib import Path
from collections import Counter

HERE   = Path(__file__).parent
SRC_DB = HERE / "transpop_poc.sqlite"
DST_DB = HERE / "transpop_poc_anon.sqlite"
K      = 2

# 1) Lecture des patients et bucketisation
conn_src = sqlite3.connect(SRC_DB)
patients = conn_src.execute("SELECT id, sexe, age FROM patients").fetchall()
conn_src.close()

def age_bucket(age):
    if age <= 40:  return "20-40"
    if age <= 60:  return "41-60"
    if age <= 80:  return "61-80"
    return "81+"

qi = [(age_bucket(a), s) for (_id, s, a) in patients]
counts = Counter(qi)

# 2) Création de la base anonymisée
conn_dst = sqlite3.connect(DST_DB)
cur_dst  = conn_dst.cursor()

# 2.1 patients_anon
cur_dst.executescript("""
DROP TABLE IF EXISTS patients_anon;
CREATE TABLE patients_anon (
    id          INTEGER PRIMARY KEY,
    age_bucket TEXT,
    sexe        TEXT
);
""")
for pid, sexe, age in patients:
    bucket = age_bucket(age)
    sexe_anon = sexe if counts[(bucket, sexe)] >= K else "U"
    cur_dst.execute(
        "INSERT INTO patients_anon (id, age_bucket, sexe) VALUES (?,?,?)",
        (pid, bucket, sexe_anon)
    )

# 2.2 Schéma explicite de antecedents
cur_dst.executescript("""
DROP TABLE IF EXISTS antecedents;
CREATE TABLE antecedents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    verbatim TEXT,
    code_cim10 TEXT,
    FOREIGN KEY(patient_id) REFERENCES patients(id)
);
""")

# 2.3 Schéma explicite de traitements
cur_dst.executescript("""
DROP TABLE IF EXISTS traitements;
CREATE TABLE traitements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    verbatim TEXT,
    code_atc TEXT,
    FOREIGN KEY(patient_id) REFERENCES patients(id)
);
""")

# 2.4 Schéma explicite de interventions
cur_dst.executescript("""
DROP TABLE IF EXISTS interventions;
CREATE TABLE interventions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    verbatim TEXT,
    code_ccam TEXT,
    FOREIGN KEY(patient_id) REFERENCES patients(id)
);
""")

# 3) Copie des données table par table
conn_src = sqlite3.connect(SRC_DB)
cur_src  = conn_src.cursor()

for tbl in ("antecedents", "traitements", "interventions"):
    rows = cur_src.execute(f"SELECT * FROM {tbl}").fetchall()
    if not rows:
        print(f"⚠️  Source {tbl} est vide ou n'existe pas")
        continue
    # prépare un placeholder par colonne
    placeholders = "(" + ",".join("?" for _ in rows[0]) + ")"
    cur_dst.executemany(
        f"INSERT INTO {tbl} VALUES {placeholders}",
        rows
    )
    print(f"✅ Copié {len(rows)} lignes dans {tbl}")

conn_src.close()
conn_dst.commit()
conn_dst.close()

print(f"[FIN] Base anonymisée générée : {DST_DB}")