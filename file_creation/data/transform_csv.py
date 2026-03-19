import csv
import json

input_file = "StockEtablissement_utf8/StockEtablissement_utf8.csv"
output_file = "entreprises.json"

entreprises = []

with open(input_file, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        # Garder seulement les établissements actifs
        if row.get("etatAdministratifEtablissement") != "A":
            continue

        # Construire un nom d'entreprise exploitable
        nom_societe = (
            row.get("denominationUsuelleEtablissement")
            or row.get("enseigne1Etablissement")
            or row.get("denominationUniteLegale")
            or ""
        ).strip()

        # Si aucun nom exploitable, on saute
        if not nom_societe:
            continue

        # Construire une adresse lisible
        adresse_parts = [
            row.get("numeroVoieEtablissement", "").strip(),
            row.get("typeVoieEtablissement", "").strip(),
            row.get("libelleVoieEtablissement", "").strip(),
        ]
        adresse_ligne = " ".join(part for part in adresse_parts if part).strip()

        ville_parts = [
            row.get("codePostalEtablissement", "").strip(),
            row.get("libelleCommuneEtablissement", "").strip(),
        ]
        ville_ligne = " ".join(part for part in ville_parts if part).strip()

        adresse_societe = ", ".join(part for part in [adresse_ligne, ville_ligne] if part)

        # Si pas de SIRET ou pas d'adresse, on saute
        if not row.get("siret") or not adresse_societe:
            continue

        entreprise = {
            "nom_societe": nom_societe,
            "adresse_societe": adresse_societe,
            "id_vendeur": row["siret"]
        }

        entreprises.append(entreprise)

        # On s'arrête dès qu'on a 500 entreprises propres
        if len(entreprises) >= 500:
            break

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(entreprises, f, indent=4, ensure_ascii=False)

print(f"Conversion terminée. {len(entreprises)} entreprises ont été écrites dans {output_file}.")