import random
import json
from faker import Faker
from datetime import timedelta

fake = Faker("fr_FR")

# Charger les catalogues
with open("data/produits.json", "r", encoding="utf-8") as f:
    catalogue_produits = json.load(f)

with open("data/services.json", "r", encoding="utf-8") as f:
    catalogue_services = json.load(f)

catalogue_global = catalogue_produits + catalogue_services


def generer_devis(entreprise):
    # ----------------------------
    # Client
    # ----------------------------
    nom_client = fake.name()

    # ----------------------------
    # Dates cohérentes
    # ----------------------------
    date_devis_obj = fake.date_between(start_date="-5y", end_date="today")
    date_prestation_obj = date_devis_obj + timedelta(days=random.randint(1, 30))

    date_devis = str(date_devis_obj)
    date_prestation = str(date_prestation_obj)

    # durée optionnelle
    duree_prestation = ""
    if random.random() < 0.5:
        duree_prestation = f"{random.randint(1, 15)} jours"

    # ----------------------------
    # Produits / services
    # ----------------------------
    produits = []
    total_ht = 0

    for _ in range(random.randint(1, 5)):
        quantite = random.randint(1, 5)
        prix_unitaire = round(random.uniform(50, 300), 2)

        produit = {
            "decompte_produit": random.choice(catalogue_global),
            "decompte_quantite": quantite,
            "decompte_unitaire": prix_unitaire
        }

        total_ht += quantite * prix_unitaire
        produits.append(produit)

    # ----------------------------
    # Champs optionnels
    # ----------------------------
    prix_main_oeuvre = 0.0
    if random.random() < 0.4:
        prix_main_oeuvre = round(random.uniform(50, 500), 2)
        total_ht += prix_main_oeuvre

    frais_deplacement = 0.0
    if random.random() < 0.3:
        frais_deplacement = round(random.uniform(10, 150), 2)
        total_ht += frais_deplacement

    total_ht = round(total_ht, 2)
    total_ttc = round(total_ht * 1.20, 2)

    devis = {
        "date_devis": date_devis,

        "nom_societe": entreprise["nom_societe"],
        "adresse_societe": entreprise["adresse_societe"],
        "id_vendeur": entreprise["id_vendeur"],

        "nom_client": nom_client,

        "date_prestation": date_prestation,
        "duree_prestation": duree_prestation,

        "produits": produits,

        "prix_main_oeuvre": prix_main_oeuvre,
        "frais_deplacement": frais_deplacement,

        "somme_ht": total_ht,
        "somme_ttc": total_ttc,

        "document_status": "real"
    }

    return devis