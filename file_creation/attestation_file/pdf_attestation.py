from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import random
import os

polices = [
    ("Helvetica", "Helvetica-Bold"),
    ("Times-Roman", "Times-Bold"),
    ("Courier", "Courier-Bold")
]

LOGO_PATH = "attestation_file/Logo_Insee.png"


def dessiner_bloc(c, x, y, largeur, hauteur, titre, font_normal, font_bold):
    # contour simple noir
    c.rect(x, y - hauteur, largeur, hauteur, stroke=1, fill=0)

    # titre du bloc
    c.setFont(font_bold, 11)
    c.drawString(x + 8, y - 16, titre)

    # ligne sous le titre
    c.line(x, y - 22, x + largeur, y - 22)


def creer_pdf_attestation_siret(attestation, chemin_pdf):
    font_normal, font_bold = random.choice(polices)

    c = canvas.Canvas(chemin_pdf, pagesize=A4)
    width, height = A4

    marge_x = 45
    y = height - 45

    # ----------------------------
    # En-tête
    # ----------------------------
    if os.path.exists(LOGO_PATH):
        c.drawImage(
            LOGO_PATH,
            marge_x,
            y - 25,
            width=90,
            height=35,
            preserveAspectRatio=True,
            mask="auto"
        )

    c.setFont(font_bold, 16)
    c.drawRightString(width - marge_x, y - 2, "Avis de situation au répertoire SIRENE")

    c.setFont(font_normal, 10)
    c.drawRightString(width - marge_x, y - 18, f"Date d'émission : {attestation['date_emission']}")

    y -= 45
    c.line(marge_x, y, width - marge_x, y)

    # ----------------------------
    # Bloc entreprise
    # ----------------------------
    y -= 20
    bloc_h = 95
    dessiner_bloc(c, marge_x, y, width - 2 * marge_x, bloc_h, "Entreprise", font_normal, font_bold)

    c.setFont(font_normal, 10)
    c.drawString(marge_x + 12, y - 40, f"Nom : {attestation['nom_societe']}")
    c.drawString(marge_x + 12, y - 56, f"Adresse : {attestation['adresse_societe']}")
    c.drawString(marge_x + 12, y - 72, f"Forme juridique : {attestation['forme_juridique']}")

    # ----------------------------
    # Bloc identification
    # ----------------------------
    y -= bloc_h + 18
    bloc_h = 90
    dessiner_bloc(c, marge_x, y, width - 2 * marge_x, bloc_h, "Identification", font_normal, font_bold)

    c.setFont(font_normal, 10)
    c.drawString(marge_x + 12, y - 40, f"SIREN : {attestation['siren']}")
    c.drawString(marge_x + 220, y - 40, f"SIRET : {attestation['siret']}")
    c.drawString(marge_x + 12, y - 58, f"Code APE : {attestation['code_ape']}")
    c.drawString(marge_x + 220, y - 58, f"État administratif : {attestation['etat_administratif']}")

    # ----------------------------
    # Bloc informations complémentaires
    # ----------------------------
    y -= bloc_h + 18
    bloc_h = 105
    dessiner_bloc(c, marge_x, y, width - 2 * marge_x, bloc_h, "Informations complémentaires", font_normal, font_bold)

    c.setFont(font_normal, 10)
    c.drawString(marge_x + 12, y - 40, f"Date de création : {attestation['date_creation']}")

    texte = f"Activité principale : {attestation['activite']}"
    text_obj = c.beginText(marge_x + 12, y - 58)
    text_obj.setFont(font_normal, 10)

    # découpe simple du texte si trop long
    max_len = 85
    while len(texte) > max_len:
        coupe = texte[:max_len]
        dernier_espace = coupe.rfind(" ")
        if dernier_espace == -1:
            dernier_espace = max_len
        text_obj.textLine(texte[:dernier_espace])
        texte = texte[dernier_espace:].strip()

    text_obj.textLine(texte)
    c.drawText(text_obj)

    # ----------------------------
    # Bloc attestation
    # ----------------------------
    y -= bloc_h + 18
    bloc_h = 80
    dessiner_bloc(c, marge_x, y, width - 2 * marge_x, bloc_h, "Attestation", font_normal, font_bold)

    texte_attestation = (
        "Le présent document atteste de l'identification de l'établissement "
        "au répertoire SIRENE à la date d'émission indiquée ci-dessus."
    )

    text_obj = c.beginText(marge_x + 12, y - 40)
    text_obj.setFont(font_normal, 10)

    max_len = 90
    while len(texte_attestation) > max_len:
        coupe = texte_attestation[:max_len]
        dernier_espace = coupe.rfind(" ")
        if dernier_espace == -1:
            dernier_espace = max_len
        text_obj.textLine(texte_attestation[:dernier_espace])
        texte_attestation = texte_attestation[dernier_espace:].strip()

    text_obj.textLine(texte_attestation)
    c.drawText(text_obj)

    # ----------------------------
    # Pied de page
    # ----------------------------
    c.line(marge_x, 55, width - marge_x, 55)

    c.setFont(font_normal, 8)
    c.drawString(marge_x, 40, "Source : Répertoire SIRENE - Document généré automatiquement")
    c.drawRightString(width - marge_x, 40, "Projet étudiant - Hackathon")

    c.save()