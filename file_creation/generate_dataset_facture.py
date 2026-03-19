import json
import os
import random

from facture_file.facture import generate_facture
from facture_file.fake_facture import falsifier_facture
from facture_file.pdf_facture import create_facture_pdf
from deterioration_pdf import creer_pdf_deteriore


# ----------------------------
# CONFIG
# ----------------------------
NB_FACTURES = 15

DOSSIER_PROPRES_VRAIES = "factures_dataset/propres/vraies"
DOSSIER_PROPRES_FAUSSES = "factures_dataset/propres/fausses"
DOSSIER_DETERIOREES_VRAIES = "factures_dataset/deteriorees/vraies"
DOSSIER_DETERIOREES_FAUSSES = "factures_dataset/deteriorees/fausses"

types_deterioration = [
    "flou",
    "scan"
]

# Création dossiers
for dossier in [
    DOSSIER_PROPRES_VRAIES,
    DOSSIER_PROPRES_FAUSSES,
    DOSSIER_DETERIOREES_VRAIES,
    DOSSIER_DETERIOREES_FAUSSES
]:
    os.makedirs(dossier, exist_ok=True)

# Charger entreprises
with open("data/entreprises.json", "r", encoding="utf-8") as f:
    entreprises = json.load(f)

# ----------------------------
# GENERATION
# ----------------------------
for i in range(NB_FACTURES):
    entreprise = entreprises[i]

    # ----------------------------
    # FACTURE VRAIE
    # ----------------------------
    facture_vraie = generate_facture(entreprise)
    nom_base_vraie = f"facture_vraie_{i+1:03d}.pdf"

    if random.random() < 0.5:
        chemin = os.path.join(DOSSIER_PROPRES_VRAIES, nom_base_vraie)
        create_facture_pdf(facture_vraie, chemin)
        print(f"✔ Vraie propre : {chemin}")
    else:
        temp = "temp.pdf"
        create_facture_pdf(facture_vraie, temp)

        type_det = random.choice(types_deterioration)
        nom_final = nom_base_vraie.replace(".pdf", f"_{type_det}.pdf")

        chemin_final = os.path.join(DOSSIER_DETERIOREES_VRAIES, nom_final)
        creer_pdf_deteriore(temp, chemin_final, type_det)

        os.remove(temp)
        print(f"🔥 Vraie détériorée : {chemin_final}")

    # ----------------------------
    # FACTURE FAUSSE
    # ----------------------------
    facture_fausse = falsifier_facture(facture_vraie)

    fraud = facture_fausse["fraud_type"]
    nom_base_fausse = f"facture_fausse_{i+1:03d}_{fraud}.pdf"

    if random.random() < 0.5:
        chemin = os.path.join(DOSSIER_PROPRES_FAUSSES, nom_base_fausse)
        create_facture_pdf(facture_fausse, chemin)
        print(f"✔ Fausse propre : {chemin}")
    else:
        temp = "temp.pdf"
        create_facture_pdf(facture_fausse, temp)

        type_det = random.choice(types_deterioration)
        nom_final = nom_base_fausse.replace(".pdf", f"_{type_det}.pdf")

        chemin_final = os.path.join(DOSSIER_DETERIOREES_FAUSSES, nom_final)
        creer_pdf_deteriore(temp, chemin_final, type_det)

        os.remove(temp)
        print(f"🔥 Fausse détériorée : {chemin_final}")