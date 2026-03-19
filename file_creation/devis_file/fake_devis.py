import copy
import random
from datetime import datetime, timedelta


def falsifier_devis(devis):
    devis_faux = copy.deepcopy(devis)

    type_falsification = random.choice([
        "siret_longueur_invalide",
        "dates_incoherentes",
        "total_negatif"
    ])

    devis_faux["document_status"] = "fake"
    devis_faux["fraud_type"] = type_falsification

    if type_falsification == "siret_longueur_invalide":
        # longueur entre 12 et 16 mais différente de 14
        longueur = random.choice([12, 13, 15, 16])
        devis_faux["id_vendeur"] = "".join(str(random.randint(0, 9)) for _ in range(longueur))

    elif type_falsification == "dates_incoherentes":
        # on part de la date_devis existante
        date_devis_obj = datetime.fromisoformat(devis_faux["date_devis"]).date()

        # écart énorme entre 7 et 15 ans
        ecart_annees = random.randint(7, 15)
        ecart_jours = ecart_annees * 365

        # parfois prestation très loin dans le futur, parfois très loin dans le passé
        if random.random() < 0.5:
            date_prestation_obj = date_devis_obj + timedelta(days=ecart_jours)
        else:
            date_prestation_obj = date_devis_obj - timedelta(days=ecart_jours)

        devis_faux["date_prestation"] = str(date_prestation_obj)

        # durée incohérente ou vide
        if "duree_prestation" in devis_faux:
            devis_faux["duree_prestation"] = f"{random.randint(1, 30)} jours"

    elif type_falsification == "total_negatif":
        devis_faux["somme_ht"] = -abs(devis_faux["somme_ht"])
        devis_faux["somme_ttc"] = -abs(devis_faux["somme_ttc"])

        if "prix_main_oeuvre" in devis_faux:
            devis_faux["prix_main_oeuvre"] = -abs(devis_faux["prix_main_oeuvre"])

        if "frais_deplacement" in devis_faux:
            devis_faux["frais_deplacement"] = -abs(devis_faux["frais_deplacement"])

    return devis_faux