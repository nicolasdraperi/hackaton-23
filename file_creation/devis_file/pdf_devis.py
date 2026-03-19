from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import random

def creer_pdf_devis(devis, chemin_pdf):
    polices = [
        ("Helvetica", "Helvetica-Bold"),
        ("Times-Roman", "Times-Bold"),
        ("Courier", "Courier-Bold")
    ]

    font_normal, font_bold = random.choice(polices)
    
    c = canvas.Canvas(chemin_pdf, pagesize=A4)
    width, height = A4

    y = height - 50

    # ----------------------------
    # Titre
    # ----------------------------
    c.setFont(font_bold, 20)
    c.drawString(50, y, "DEVIS")

    # ----------------------------
    # Informations générales
    # ----------------------------
    y -= 40
    c.setFont(font_normal, 11)
    c.drawString(50, y, f"Date du devis : {devis['date_devis']}")

    y -= 20
    c.drawString(50, y, f"Date de prestation : {devis['date_prestation']}")

    y -= 20
    c.drawString(50, y, f"Durée de prestation : {devis['duree_prestation']}")

    # ----------------------------
    # Bloc société
    # ----------------------------
    y -= 40
    c.setFont(font_bold, 12)
    c.drawString(50, y, "Société")

    y -= 20
    c.setFont(font_normal, 11)
    c.drawString(50, y, devis["nom_societe"])

    y -= 20
    c.drawString(50, y, devis["adresse_societe"])

    y -= 20
    c.drawString(50, y, f"SIRET : {devis['id_vendeur']}")

    # ----------------------------
    # Bloc client
    # ----------------------------
    y -= 40
    c.setFont(font_bold, 12)
    c.drawString(50, y, "Client")

    y -= 20
    c.setFont(font_normal, 11)
    c.drawString(50, y, devis["nom_client"])

    # ----------------------------
    # Tableau produits / services
    # ----------------------------
    y -= 40
    c.setFont(font_bold, 11)
    c.drawString(50, y, "Produit / Service")
    c.drawString(280, y, "Quantité")
    c.drawString(380, y, "Prix unitaire")

    y -= 10
    c.line(50, y, 550, y)

    y -= 20
    c.setFont(font_normal, 10)

    for produit in devis["produits"]:
        nom_produit = produit["decompte_produit"][:40]
        quantite = str(produit["decompte_quantite"])
        prix = f"{produit['decompte_unitaire']:.2f} €"

        c.drawString(50, y, nom_produit)
        c.drawString(280, y, quantite)
        c.drawString(380, y, prix)

        y -= 20

        # Nouvelle page si besoin
        if y < 120:
            c.showPage()
            y = height - 50

            c.setFont(font_bold, 11)
            c.drawString(50, y, "Produit / Service")
            c.drawString(280, y, "Quantité")
            c.drawString(380, y, "Prix unitaire")

            y -= 10
            c.line(50, y, 550, y)
            y -= 20
            c.setFont(font_normal, 10)

    # ----------------------------
    # Main d'oeuvre / déplacement
    # ----------------------------
    y -= 20
    c.setFont(font_normal, 11)
    c.drawString(50, y, f"Prix main d'oeuvre : {devis['prix_main_oeuvre']:.2f} €")

    y -= 20
    c.drawString(50, y, f"Frais de déplacement : {devis['frais_deplacement']:.2f} €")

    # ----------------------------
    # Totaux
    # ----------------------------
    y -= 30
    c.line(300, y, 550, y)

    y -= 25
    c.setFont(font_bold, 11)
    c.drawString(350, y, f"Total HT : {devis['somme_ht']:.2f} €")

    y -= 20
    c.drawString(350, y, f"Total TTC : {devis['somme_ttc']:.2f} €")

    c.save()