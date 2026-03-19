import random
import json
from faker import Faker

fake = Faker("fr_FR")

FORMES_JURIDIQUES = [
    "SAS", "SARL", "EURL", "SA", "Micro-entreprise",
    "Entreprise individuelle", "SASU"
]

ETATS_ADMIN = [
    "Active",
    "En activité"
]

CODES_APE = [
    "47.11A", "62.01Z", "70.22Z", "46.90Z", "68.20B",
    "43.21A", "85.59A", "74.10Z", "82.11Z", "96.09Z"
]

with open("data/activites.json", "r", encoding="utf-8") as f:
    ACTIVITES = json.load(f)


def generer_attestation_siret(entreprise):
    siret = entreprise["id_vendeur"]
    siren = siret[:9]

    date_emission_obj = fake.date_between(start_date="-5y", end_date="today")
    date_creation_obj = fake.date_between(start_date="-15y", end_date=date_emission_obj)

    attestation = {
        "date_emission": str(date_emission_obj),
        "nom_societe": entreprise["nom_societe"],
        "adresse_societe": entreprise["adresse_societe"],
        "siren": siren,
        "siret": siret,
        "code_ape": random.choice(CODES_APE),
        "activite": random.choice(ACTIVITES),
        "forme_juridique": random.choice(FORMES_JURIDIQUES),
        "date_creation": str(date_creation_obj),
        "etat_administratif": random.choice(ETATS_ADMIN),
        "document_status": "real"
    }

    return attestation