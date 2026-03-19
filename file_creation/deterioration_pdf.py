import os
import random
import fitz
from PIL import Image, ImageFilter, ImageEnhance


def convertir_pdf_en_image(chemin_pdf):
    doc = fitz.open(chemin_pdf)
    page = doc.load_page(0)

    pix = page.get_pixmap(dpi=150)
    image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    return image


def image_vers_pdf(image, chemin_pdf):
    image.save(chemin_pdf, "PDF", resolution=150.0)


# ----------------------------
# FLOU
# ----------------------------
def appliquer_flou(image):
    rayon = random.uniform(0.9, 1.6)
    return image.filter(ImageFilter.GaussianBlur(radius=rayon))


# ----------------------------
# SCAN
# ----------------------------
def appliquer_rotation_scan(image):
    angle = random.uniform(-4.5, 4.5)
    return image.rotate(angle, expand=True, fillcolor="white")


def appliquer_redimensionnement_scan(image):
    largeur, hauteur = image.size

    facteur_global = random.uniform(0.88, 1.00)
    facteur_x = random.uniform(0.94, 1.06)
    facteur_y = random.uniform(0.94, 1.06)

    nouvelle_largeur = max(1, int(largeur * facteur_global * facteur_x))
    nouvelle_hauteur = max(1, int(hauteur * facteur_global * facteur_y))

    image_redim = image.resize(
        (nouvelle_largeur, nouvelle_hauteur),
        Image.Resampling.BICUBIC
    )

    fond = Image.new("RGB", (largeur, hauteur), "white")

    marge_x = max(0, largeur - nouvelle_largeur)
    marge_y = max(0, hauteur - nouvelle_hauteur)

    x = random.randint(0, marge_x) if marge_x > 0 else 0
    y = random.randint(0, marge_y) if marge_y > 0 else 0

    fond.paste(image_redim, (x, y))
    return fond


def appliquer_teinte_jaunie(image):
    intensite = random.uniform(0.04, 0.12)

    image = image.convert("RGB")
    pixels = image.load()
    largeur, hauteur = image.size

    for x in range(largeur):
        for y in range(hauteur):
            r, g, b = pixels[x, y]

            r = min(255, int(r + 255 * intensite * 0.55))
            g = min(255, int(g + 255 * intensite * 0.35))
            b = max(0, int(b - 255 * intensite * 0.25))

            pixels[x, y] = (r, g, b)

    return image


def appliquer_contraste_scan(image):
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(random.uniform(0.86, 0.97))


def appliquer_luminosite_scan(image):
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(random.uniform(0.94, 1.04))


def simuler_scan(image):
    image = appliquer_rotation_scan(image)
    image = appliquer_redimensionnement_scan(image)

    if random.random() < 0.85:
        image = appliquer_teinte_jaunie(image)

    if random.random() < 0.75:
        image = appliquer_contraste_scan(image)

    if random.random() < 0.45:
        image = appliquer_luminosite_scan(image)

    if random.random() < 0.30:
        image = image.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.25, 0.6)))

    return image


# ----------------------------
# MAIN
# ----------------------------
def deteriorer_image(image, type_det):
    if type_det == "flou":
        return appliquer_flou(image)

    if type_det == "scan":
        return simuler_scan(image)

    return image


def creer_pdf_deteriore(chemin_pdf_entree, chemin_pdf_sortie, type_det):
    image = convertir_pdf_en_image(chemin_pdf_entree)
    image = deteriorer_image(image, type_det)

    os.makedirs(os.path.dirname(chemin_pdf_sortie), exist_ok=True)
    image_vers_pdf(image, chemin_pdf_sortie)