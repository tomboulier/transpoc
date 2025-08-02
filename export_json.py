import sqlite3
import json
import argparse
from pathlib import Path

def export_patients(db_path: Path, output_path: Path, patient_ids=None):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if patient_ids:
        placeholders = ','.join('?' for _ in patient_ids)
        query = f"SELECT id, sexe, age FROM patients WHERE id IN ({placeholders})"
        cursor.execute(query, patient_ids)
    else:
        cursor.execute("SELECT id, sexe, age FROM patients")

    patients = []
    for pid, sexe, age in cursor.fetchall():
        cursor.execute("SELECT verbatim FROM antecedents WHERE patient_id = ?", (pid,))
        antecedents = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT verbatim FROM traitements WHERE patient_id = ?", (pid,))
        traitements = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT verbatim FROM interventions WHERE patient_id = ?", (pid,))
        row = cursor.fetchone()
        intervention = row[0] if row else None

        patients.append({
            "id": pid,
            "sexe": sexe,
            "age": age,
            "antecedents": antecedents,
            "traitements": traitements,
            "intervention": intervention
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(patients, f, indent=2, ensure_ascii=False)

    print(f"Exported {len(patients)} patients to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Exporter des patients depuis une base SQLite vers JSON")
    parser.add_argument("--db", required=True, help="Chemin vers la base SQLite")
    parser.add_argument("--output", required=True, help="Chemin du fichier JSON de sortie")
    parser.add_argument("--all", action="store_true", help="Exporter tous les patients")
    parser.add_argument("--id", nargs="+", type=int, help="IDs des patients à exporter")

    args = parser.parse_args()

    if not args.all and not args.id:
        parser.error("Spécifiez --all ou --id <ID1> <ID2> ...")

    export_patients(Path(args.db), Path(args.output), args.id if args.id else None)

if __name__ == "__main__":
    main()