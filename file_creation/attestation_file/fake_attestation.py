import copy
import random
from faker import Faker

fake = Faker("fr_FR")


def falsifier_attestation_siret(attestation):
    attestation_fausse = copy.deepcopy(attestation)

    type_falsification = random.choice([
        "siret_longueur_invalide",
        "siren_absent_du_siret",
        "nom_societe_faux",
        "adresse_societe_fausse"
    ])

    attestation_fausse["document_status"] = "fake"
    attestation_fausse["fraud_type"] = type_falsification

    if type_falsification == "siret_longueur_invalide":
        longueur = random.choice([12, 13, 15, 16])
        attestation_fausse["siret"] = "".join(str(random.randint(0, 9)) for _ in range(longueur))

    elif type_falsification == "siren_absent_du_siret":
        faux_siren = "".join(str(random.randint(0, 9)) for _ in range(9))
        nic = "".join(str(random.randint(0, 9)) for _ in range(5))

        while faux_siren == attestation_fausse["siren"]:
            faux_siren = "".join(str(random.randint(0, 9)) for _ in range(9))

        attestation_fausse["siret"] = faux_siren + nic

    elif type_falsification == "nom_societe_faux":
        attestation_fausse["nom_societe"] = fake.company()

    elif type_falsification == "adresse_societe_fausse":
        attestation_fausse["adresse_societe"] = fake.address().replace("\n", ", ")

    return attestation_fausse