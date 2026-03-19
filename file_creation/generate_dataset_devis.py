import json
import os
import random

from devis_file.devis import generer_devis
from devis_file.fake_devis import falsifier_devis
from devis_file.pdf_devis import creer_pdf_devis
from deterioration_pdf import creer_pdf_deteriore

# ----------------------------
# CONFIG
# ----------------------------
NB_DEVIS = 15

DOSSIER_PROPRES_VRAIS = "devis_dataset/propres/vrais"
DOSSIER_PROPRES_FAUX = "devis_dataset/propres/faux"
DOSSIER_DETERIORES_VRAIS = "devis_dataset/deteriores/vrais"
DOSSIER_DETERIORES_FAUX = "devis_dataset/deteriores/faux"

types_deterioration = [
    "flou",
    "scan"
]

# Création dossiers
for dossier in [
    DOSSIER_PROPRES_VRAIS,
    DOSSIER_PROPRES_FAUX,
    DOSSIER_DETERIORES_VRAIS,
    DOSSIER_DETERIORES_FAUX
]:
    os.makedirs(dossier, exist_ok=True)

# Charger entreprises
with open("data/entreprises.json", "r", encoding="utf-8") as f:
    entreprises = json.load(f)

# ----------------------------
# GENERATION
# ----------------------------
for i in range(NB_DEVIS):
    entreprise = entreprises[i]

    # ----------------------------
    # DEVIS VRAI
    # ----------------------------
    devis_vrai = generer_devis(entreprise)
    nom_base_vrai = f"devis_vrai_{i+1:03d}.pdf"

    if random.random() < 0.5:
        chemin = os.path.join(DOSSIER_PROPRES_VRAIS, nom_base_vrai)
        creer_pdf_devis(devis_vrai, chemin)
        print(f"✔ Devis vrai propre : {chemin}")
    else:
        temp = "temp.pdf"
        creer_pdf_devis(devis_vrai, temp)

        type_det = random.choice(types_deterioration)
        nom_final = nom_base_vrai.replace(".pdf", f"_{type_det}.pdf")

        chemin_final = os.path.join(DOSSIER_DETERIORES_VRAIS, nom_final)
        creer_pdf_deteriore(temp, chemin_final, type_det)

        os.remove(temp)
        print(f"🔥 Devis vrai détérioré : {chemin_final}")

    # ----------------------------
    # DEVIS FAUX
    # ----------------------------
    devis_faux = falsifier_devis(devis_vrai)

    fraud = devis_faux["fraud_type"]
    nom_base_faux = f"devis_faux_{i+1:03d}_{fraud}.pdf"

    if random.random() < 0.5:
        chemin = os.path.join(DOSSIER_PROPRES_FAUX, nom_base_faux)
        creer_pdf_devis(devis_faux, chemin)
        print(f"✔ Devis faux propre : {chemin}")
    else:
        temp = "temp.pdf"
        creer_pdf_devis(devis_faux, temp)

        type_det = random.choice(types_deterioration)
        nom_final = nom_base_faux.replace(".pdf", f"_{type_det}.pdf")

        chemin_final = os.path.join(DOSSIER_DETERIORES_FAUX, nom_final)
        creer_pdf_deteriore(temp, chemin_final, type_det)

        os.remove(temp)
        print(f"🔥 Devis faux détérioré : {chemin_final}")