import json
import os
import random

from attestation_file.attestation import generer_attestation_siret
from attestation_file.fake_attestation import falsifier_attestation_siret
from attestation_file.pdf_attestation import creer_pdf_attestation_siret
from deterioration_pdf import creer_pdf_deteriore

NB_ATTESTATIONS = 10

DOSSIER_PROPRES_VRAIES = "attestation_siret_dataset/propres/vraies"
DOSSIER_PROPRES_FAUSSES = "attestation_siret_dataset/propres/fausses"
DOSSIER_DETERIOREES_VRAIES = "attestation_siret_dataset/deteriorees/vraies"
DOSSIER_DETERIOREES_FAUSSES = "attestation_siret_dataset/deteriorees/fausses"

types_deterioration = [
    "flou",
    "scan"
]

for dossier in [
    DOSSIER_PROPRES_VRAIES,
    DOSSIER_PROPRES_FAUSSES,
    DOSSIER_DETERIOREES_VRAIES,
    DOSSIER_DETERIOREES_FAUSSES
]:
    os.makedirs(dossier, exist_ok=True)

with open("data/entreprises.json", "r", encoding="utf-8") as f:
    entreprises = json.load(f)

for i in range(NB_ATTESTATIONS):
    entreprise = entreprises[i]

    # vraie
    attestation_vraie = generer_attestation_siret(entreprise)
    nom_base_vraie = f"attestation_siret_vraie_{i+1:03d}.pdf"

    if random.random() < 0.5:
        chemin = os.path.join(DOSSIER_PROPRES_VRAIES, nom_base_vraie)
        creer_pdf_attestation_siret(attestation_vraie, chemin)
        print(f"Attestation vraie propre : {chemin}")
    else:
        temp = "temp.pdf"
        creer_pdf_attestation_siret(attestation_vraie, temp)

        type_det = random.choice(types_deterioration)
        nom_final = nom_base_vraie.replace(".pdf", f"_{type_det}.pdf")

        chemin_final = os.path.join(DOSSIER_DETERIOREES_VRAIES, nom_final)
        creer_pdf_deteriore(temp, chemin_final, type_det)

        os.remove(temp)
        print(f"Attestation vraie détériorée : {chemin_final}")

    # fausse
    attestation_fausse = falsifier_attestation_siret(attestation_vraie)
    fraud = attestation_fausse["fraud_type"]
    nom_base_fausse = f"attestation_siret_fausse_{i+1:03d}_{fraud}.pdf"

    if random.random() < 0.5:
        chemin = os.path.join(DOSSIER_PROPRES_FAUSSES, nom_base_fausse)
        creer_pdf_attestation_siret(attestation_fausse, chemin)
        print(f"Attestation fausse propre : {chemin}")
    else:
        temp = "temp.pdf"
        creer_pdf_attestation_siret(attestation_fausse, temp)

        type_det = random.choice(types_deterioration)
        nom_final = nom_base_fausse.replace(".pdf", f"_{type_det}.pdf")

        chemin_final = os.path.join(DOSSIER_DETERIOREES_FAUSSES, nom_final)
        creer_pdf_deteriore(temp, chemin_final, type_det)

        os.remove(temp)
        print(f"Attestation fausse détériorée : {chemin_final}")