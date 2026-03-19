from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import random

def create_facture_pdf(facture, chemin_pdf):
    polices = [
        ("Helvetica", "Helvetica-Bold"),
        ("Times-Roman", "Times-Bold"),
        ("Courier", "Courier-Bold") 
    ]

    font_normal, font_bold = random.choice(polices)

    c = canvas.Canvas(chemin_pdf, pagesize=A4)
    width, height = A4

    # Position de départ en haut de page
    y = height - 50

    # ----------------------------
    # Titre
    # ----------------------------
    c.setFont(font_bold, 20)
    c.drawString(50, y, "FACTURE")

    # ----------------------------
    # Informations générales
    # ----------------------------
    y -= 40
    c.setFont(font_normal, 11)
    c.drawString(50, y, f"Numéro de facture : {facture['id_facture']}")
    y -= 20
    c.drawString(50, y, f"Date d'émission : {facture['date_emission']}")
    y -= 20
    c.drawString(50, y, f"Date de la facture : {facture['date_facture']}")
    y -= 20
    c.drawString(50, y, f"Commande : {facture['id_commande']}")

    # ----------------------------
    # Bloc vendeur
    # ----------------------------
    y -= 40
    c.setFont(font_bold, 12)
    c.drawString(50, y, "Vendeur")

    y -= 20
    c.setFont(font_normal, 11)
    c.drawString(50, y, facture["nom_vendeur"])
    y -= 20
    c.drawString(50, y, facture["adresse_vendeur"])
    y -= 20
    c.drawString(50, y, f"SIRET : {facture['id_vendeur']}")
    y -= 20
    c.drawString(50, y, f"TVA : {facture['id_tva']}")

    # ----------------------------
    # Bloc client
    # ----------------------------
    y -= 40
    c.setFont(font_bold, 12)
    c.drawString(50, y, "Client")

    y -= 20
    c.setFont(font_normal, 11)
    c.drawString(50, y, facture["nom_client"])
    y -= 20
    c.drawString(50, y, facture["adresse_client"])
    y -= 20
    c.drawString(50, y, f"ID Client : {facture['id_client']}")
    y -= 20
    c.drawString(50, y, f"Adresse de facturation : {facture['adresse_fac']}")

    # ----------------------------
    # Tableau produits
    # ----------------------------
    y -= 40
    c.setFont(font_bold, 11)
    c.drawString(50, y, "Produit")
    c.drawString(260, y, "Quantité")
    c.drawString(330, y, "Prix unitaire")
    c.drawString(450, y, "TVA")

    y -= 10
    c.line(50, y, 550, y)

    y -= 20
    c.setFont(font_normal, 10)

    for produit in facture["produits"]:
        nom_produit = produit["nom_produit"][:35]
        quantite = str(produit["quantite_produit"])
        prix = f"{produit['prix_produit']:.2f} €"
        tva = f"{produit['taux_tva_produit'] * 100:.0f}%"

        c.drawString(50, y, nom_produit)
        c.drawString(260, y, quantite)
        c.drawString(330, y, prix)
        c.drawString(450, y, tva)

        y -= 20

        # Si on arrive trop bas, nouvelle page
        if y < 120:
            c.showPage()
            y = height - 50
            c.setFont(font_bold, 11)
            c.drawString(50, y, "Produit")
            c.drawString(260, y, "Quantité")
            c.drawString(330, y, "Prix unitaire")
            c.drawString(450, y, "TVA")
            y -= 10
            c.line(50, y, 550, y)
            y -= 20
            c.setFont(font_normal, 10)

    # ----------------------------
    # Totaux
    # ----------------------------
    y -= 20
    c.line(300, y, 550, y)

    y -= 25
    c.setFont(font_bold, 11)
    c.drawString(350, y, f"Total HT : {facture['somme_ht']:.2f} €")
    y -= 20
    c.drawString(350, y, f"Réduction : {facture['reduction_prix']:.2f} €")
    y -= 20
    c.drawString(350, y, f"Total TTC : {facture['somme_ttc']:.2f} €")

    # ----------------------------
    # Paiement
    # ----------------------------
    y -= 40
    c.setFont(font_bold, 12)
    c.drawString(50, y, "Paiement")

    y -= 20
    c.setFont(font_normal, 11)
    c.drawString(50, y, f"Date de paiement : {facture['date_paiement']}")
    y -= 20
    c.drawString(50, y, f"Conditions d'escompte : {facture['conditions_escompte']}")
    y -= 20
    c.drawString(50, y, f"Taux de pénalités : {facture['taux_penalites']}")
    y -= 20
    c.drawString(50, y, f"Indemnité forfaitaire : {facture['indemnite_forfaitaire']}")

    c.save()