import copy
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker("fr_FR")


def falsifier_facture(facture):
    facture_fausse = copy.deepcopy(facture)

    type_falsification = random.choice([
        "siret_longueur_invalide",
        "tva_format_invalide",
        "dates_incoherentes",
        "siren_absent_tva",
        "montant_ttc_negatif",
        "identite_entreprise_fausse"
    ])

    facture_fausse["document_status"] = "fake"
    facture_fausse["fraud_type"] = type_falsification

    if type_falsification == "siret_longueur_invalide":
        longueur = random.choice([12, 13, 15, 16])
        facture_fausse["id_vendeur"] = "".join(str(random.randint(0, 9)) for _ in range(longueur))

    elif type_falsification == "tva_format_invalide":
        longueur = random.choice([11, 12, 14, 15])
        prefixe = random.choice(["DE", "XX", "", "IT", "ES"])
        reste = "".join(str(random.randint(0, 9)) for _ in range(max(longueur - len(prefixe), 0)))
        facture_fausse["id_tva"] = prefixe + reste

    elif type_falsification == "dates_incoherentes":
        date_facture = datetime.fromisoformat(facture_fausse["date_facture"]).date()
        date_emission = date_facture + timedelta(days=random.randint(5, 20))
        date_paiement = date_facture - timedelta(days=random.randint(1, 20))

        facture_fausse["date_facture"] = str(date_facture)
        facture_fausse["date_emission"] = str(date_emission)
        facture_fausse["date_paiement"] = str(date_paiement)

    elif type_falsification == "siren_absent_tva":
        faux_siren = "".join(str(random.randint(0, 9)) for _ in range(9))
        vrai_siren = facture_fausse["id_vendeur"][:9]

        while faux_siren == vrai_siren:
            faux_siren = "".join(str(random.randint(0, 9)) for _ in range(9))

        cle_tva = f"{random.randint(0, 99):02d}"
        facture_fausse["id_tva"] = f"FR{cle_tva}{faux_siren}"

    elif type_falsification == "montant_ttc_negatif":
        facture_fausse["somme_ttc"] = -abs(facture_fausse["somme_ttc"])

    elif type_falsification == "identite_entreprise_fausse":
        facture_fausse["nom_vendeur"] = fake.company()
        facture_fausse["adresse_vendeur"] = fake.address().replace("\n", ", ")

    return facture_fausse