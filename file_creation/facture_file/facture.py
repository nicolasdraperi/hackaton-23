import random
import json
from faker import Faker
from datetime import datetime, timedelta

fake = Faker("fr_FR")

# Charger les catalogues une seule fois au démarrage
with open("data/produits.json", "r", encoding="utf-8") as f:
    catalogue_produits = json.load(f)

with open("data/services.json", "r", encoding="utf-8") as f:
    catalogue_services = json.load(f)

catalogue_global = catalogue_produits + catalogue_services


def generate_facture(entreprise):

    siren = entreprise["id_vendeur"][:9]
    siren_int = int(siren)

    cle_tva = (12 + 3 * (siren_int % 97)) % 97

    id_tva = f"FR{cle_tva:02d}{siren}"
    # ----------------------------
    # Générer un client
    # ----------------------------
    nom_client = fake.name()
    adresse_client = fake.address().replace("\n", ", ")
    adresse_facturation = adresse_client

    # ----------------------------
    # Générer des dates cohérentes
    # ----------------------------
    # date_facture = date de prestation / vente
    date_facture_obj = fake.date_between(start_date="-10y", end_date="-5d")

    # date_emission = même jour ou quelques jours après la date_facture
    date_emission_obj = date_facture_obj + timedelta(days=random.randint(0, 5))

    # date_paiement = après l'émission
    date_paiement_obj = date_emission_obj + timedelta(days=random.randint(15, 45))

    date_facture = str(date_facture_obj)
    date_emission = str(date_emission_obj)
    date_paiement = str(date_paiement_obj)

    # ----------------------------
    # Générer les produits / services
    # ----------------------------
    produits = []
    total_ht = 0

    for _ in range(random.randint(1, 5)):
        quantite = random.randint(1, 10)
        prix_unitaire = round(random.uniform(10, 300), 2)
        taux_tva = 0.20

        nom_produit = random.choice(catalogue_global)

        produit = {
            "quantite_produit": quantite,
            "nom_produit": nom_produit,
            "prix_produit": prix_unitaire,
            "taux_tva_produit": taux_tva
        }

        total_ligne = quantite * prix_unitaire
        total_ht += total_ligne
        produits.append(produit)

    total_ht = round(total_ht, 2)
    total_ttc = round(total_ht * 1.20, 2)

    # ----------------------------
    # Construire la facture
    # ----------------------------
    facture = {
        "date_emission": date_emission,
        "id_facture": f"FAC-{fake.unique.random_int(min=100000, max=999999)}",
        "date_facture": date_facture,

        "nom_vendeur": entreprise["nom_societe"],
        "adresse_vendeur": entreprise["adresse_societe"],
        "id_vendeur": entreprise["id_vendeur"],

        "nom_client": nom_client,
        "adresse_client": adresse_client,
        "id_client": f"CLI-{fake.random_int(min=1000, max=9999)}",

        "id_commande": f"CMD-{fake.random_int(min=10000, max=99999)}",
        "id_tva": id_tva,

        "produits": produits,

        "somme_ht": total_ht,
        "somme_ttc": total_ttc,
        "reduction_prix": 0.0,

        "adresse_fac": adresse_facturation,

        "date_paiement": date_paiement,
        "conditions_escompte": "",
        "taux_penalites": "",
        "indemnite_forfaitaire": ""
    }

    return facture