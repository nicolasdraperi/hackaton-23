# OpenCV : traitement d'image
import cv2

# EasyOCR : moteur OCR
import easyocr

# re : expressions régulières pour extraire les informations
import re

import json

from pdf2image import convert_from_path
import numpy as np

import os
import tempfile

from datetime import datetime
from datetime import timedelta
from .validation import validate_document

# chemin du document à analyser
# file_paths = ["devis/propres/vrais/devis_vrai_002.pdf"]
reader = easyocr.Reader(['fr'], gpu=False)

all_results = []
def run_ocr(file):
    # updated to handle file upload in Django
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        for chunk in file.chunks():
            tmp.write(chunk)
        file_path = tmp.name

    file_paths = [file_path]

    for file_path in file_paths:
        images_to_process = []

        ext = os.path.splitext(file_path)[1].lower()

        # prétraitement du/des fichiers
        # PDF
        if ext == ".pdf":
            
            pages = convert_from_path(file_path, dpi=300, poppler_path="/opt/homebrew/bin")

            for page in pages:
                image = np.array(page)
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                images_to_process.append(image)

        # IMAGE
        else:
            # lecture de l'image
            image = cv2.imread(file_path)

        images_to_process.append(image)

    # préparation des images
    for i, image in enumerate(images_to_process):

        # agrandir l'image pour améliorer la précision OCR
        image = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

        # convertir l'image en niveaux de gris
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # suppression du bruit
        gray = cv2.GaussianBlur(gray, (5,5), 0)

        # binarisation (texte noir / fond blanc)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

        # exécuter l'OCR
        results = reader.readtext(thresh)


        texts = []
        ocr_data = []
        # stockage des résultats
        for bbox, text, confidence in results:
            """
            bbox -> position dans l'image
            text -> texte reconnu
            confidence -> score de confiance (entre 0 et 1)
            """

            # stocker le texte pour reconstruire le document
            texts.append(text)

            # stocker texte + confiance dans une structure
            ocr_data.append({
                "text": text,
                "confidence": confidence
            })

    # reconstruire un texte unique pour faciliter l'utilisation des regex
    full_text = " ".join(texts)

    # extraction des données
    extracted_data = {}
    text = full_text.lower()
    print(text)

    # definition du type de document
    score_facture = 0
    score_devis = 0
    score_attestation = 0

    if re.search(r"facture", text):
        score_facture += 3
    if re.search(r"total\s*ttc", text):
        score_facture += 2

    if re.search(r"d[eé]v[i1l]s", text):
        score_devis += 3

    if re.search(r"attestation", text, re.IGNORECASE):
        score_attestation += 3

    if score_attestation > score_facture and score_attestation > score_devis:
        document_type = "attestation"
    elif score_devis > score_facture:
        document_type = "devis"
    elif score_facture > 0:
        document_type = "facture"
    else:
        document_type = "inconnu"


    # stockage
    extracted_data["document_type"] = document_type


    # correction des nombres
    def clean_digits(text):
        """
        Nettoyage des chiffres :
        - corrige les erreurs courantes (O→0, I→1)
        - supprime tout sauf les chiffres
        """
        text = text.replace("O", "0").replace("o", "0")
        text = text.replace("I", "1").replace("l", "1")

        # enlever tout sauf les chiffres
        text = re.sub(r"\D", "", text)

        return text


    # EXTRACTION DES INFORMATIONS

    # DATES

    def parse_date(date_str):
        """
        Convertit une chaîne en date en testant plusieurs formats et retourne la date si valide.
        """
        formats = [
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%Y-%m-%d"
            ]

        for format in formats:
            try:
                return datetime.strptime(date_str, format)
            except:
                continue

        return None


    # accepter plusieurs formats de dates valides
    date_patterns = [
        r"\b\d{2}[/-]\d{2}[/-]\d{4}\b",
        r"\b\d{4}-\d{2}-\d{2}\b",
        r"\b\d{1,2}\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{4}\b"
    ]
    
    def extract_date(context_pattern, label):
        """
        Extrait une date du texte OCR en fonction d’un contexte (ex : "date facture").

        Teste plusieurs formats de dates, valide le résultat, calcule un score de confiance
        à partir des données OCR, puis stocke le résultat dans `extracted_data`.

        Retourne un objet structuré avec : value, valid, missing, confidence.
        """

        for date_pattern in date_patterns:

            full_pattern = context_pattern + r"[^0-9]*(" + date_pattern + ")"

            match = re.search(full_pattern, full_text, re.IGNORECASE)

            if match:
                value = match.group(1)

                parsed = parse_date(value)
                is_valid = parsed is not None

                # calcul confidence
                scores = []
                for item in ocr_data:
                    if item["text"] in value:
                        scores.append(item["confidence"])

                confidence = sum(scores) / len(scores) if scores else None

                # stockage
                extracted_data[label] = {
                    "value": value,
                    "valid": is_valid,
                    "missing": False,
                    "confidence": confidence
                }

                return 
        # si aucune date n'est trouvée
        extracted_data[label] = {
            "value": None,
            "valid": False,
            "missing": True,
            "confidence": None
        }

    # documents détériorés peuvent entrainer une inversion dans les élements du titre, les regex accepte des élements inversés. ex : date paiement/date de paiement/paiement date/paiement date de/paiement
    if document_type == "facture":
        extract_date(
            r"(?:date\s*d['’]?\s*émission|émission\s*date)",
            "date_emission"
        )

        extract_date(
            r"(?:date\s*(?:de\s*)?(?:la\s*)?facture|facture\s*date)",
            "date_facture"
        )

        extract_date(
            r"(?:date\s*(?:de\s*)?paiement|paiement\s*date\s*(?:de\s*)?|paiement)",
            "date_paiement"
        )

    if document_type == "devis":
        extract_date(
        r"(?:date\s*(?:du\s*)?d[eé]v[i1l]s|d[eé]v[i1l]s\s*date)",
        "date_devis"
        )

        extract_date(
        r"(?:date\s*(?:de\s*)?presta[t7][i1]on|presta[t7][i1]on\s*date)",
        "date_prestation"
        )


    # Vérification incohérence de dates
    date_issues = []

    def get_date(field):
        if field in extracted_data:
            return parse_date(extracted_data[field]["value"])
        return None

    date_facture = get_date("date_facture")
    date_paiement = get_date("date_paiement")
    date_devis = get_date("date_devis")
    date_prestation = get_date("date_prestation")

    if date_facture and date_paiement:
        if date_paiement <= date_facture:
            date_issues.append("date paiement antérieure à la date facture")

    if date_prestation and date_devis:
        if date_prestation < date_devis:
            date_issues.append("date prestation antérieure à la date devis")

    def validate_dates(date_devis, date_prestation):
        if not date_devis or not date_prestation:
            return None 

        # différence en jours
        delta = date_prestation - date_devis

        # 7 ans ≈ 2555 jours
        max_delta = timedelta(days=365 * 7)

        return timedelta(days=0) <= delta <= max_delta

    # vérifie que le delta entre date prestation et date devis inférieur à 7 ans
    is_valid = validate_dates(date_devis, date_prestation)

    if is_valid is False:
        date_issues.append("date prestation dépasse de plus de 7 ans la date du devis")

    # stockage de l'erreur de date
    if date_issues:
        extracted_data["date_inconsistencies"] = date_issues


    # NUMERO DE FACTURE

    if document_type == "facture":
        facture_number = re.search(r"\b[A-Z]{2,5}-\d+(?:-\d+)?\b", text, re.IGNORECASE)

        if facture_number:
            facture_value = facture_number.group()
            facture_conf = None

            for item in ocr_data:
                if item["text"] == facture_value:
                    facture_conf = item["confidence"]

            extracted_data["numero_facture"] = {
                "value": facture_value,
                "confidence": facture_conf,
                "missing": False,
                "valid": True
            }
        else:
            extracted_data["numero_facture"] = {
                "value": None,
                "confidence": None,
                "missing": True,
                "valid": False
            }


    #  SIRET

    # recherche un numéro lié au nom siret
    siret_match = re.search(r"siret[^0-9]*(\d{9,16})", text, re.IGNORECASE)

    if siret_match:
        siret_raw = siret_match.group(1)

        siret_value = clean_digits(siret_raw)
    
        # validation du nombre de caractères
        is_valid_siret = len(siret_value) == 14

        siret_conf = None
        for item in ocr_data:
            if siret_value in item["text"]:
                siret_conf = item["confidence"]

        extracted_data["siret"] = {
            "value": siret_value,
            "valid": is_valid_siret,
            "confidence": siret_conf,
            "missing": False
        }
    else:
        extracted_data["siret"] = {
            "value": None,
            "confidence": None,
            "missing": True,
            "valid": False
        }


    #  SIREN

    siren_value = None
    siren_conf = None
    is_valid_siren = False
    missing = True
    siren_in_siret_match = None

    # recherche SIREN
    siren_match = re.search(r"siren[^0-9]*(\d{7,15})", text, re.IGNORECASE)

    # si pas trouvé recherche SIRET
    siret_match = re.search(r"siret[^0-9]*(\d{12,20})", text, re.IGNORECASE)

    if siren_match:
        siren_raw = siren_match.group(1)
        siren_value = clean_digits(siren_raw)
        missing = False
    # extraction du SIREN via le SIRET
    elif siret_match:
        siret_raw = siret_match.group(1)
        siret_value = clean_digits(siret_raw)
        siren_value = siret_value[:9]
        missing = False

    if not siren_value:
        fallback_match = re.search(r"\b\d{9}\b", text)
        if fallback_match:
            siren_value = clean_digits(fallback_match.group())
            missing = False

    # validation
    if siren_value:
        is_valid_siren = len(siren_value) == 9

    if siren_value and siret_value and len(siret_value) >= 9:
        siren_in_siret_match = (siren_value == siret_value[:9])

    # confiance
    scores = []

    for item in ocr_data:
        cleaned_text = clean_digits(item["text"])
        if siren_value and siren_value in cleaned_text:
                scores.append(item["confidence"])
    siren_conf = sum(scores) / len(scores) if scores else None

    # stockage
    extracted_data["siren"] = {
        "value": siren_value,
        "valid": is_valid_siren,
        "confidence": siren_conf,
        "missing": missing,
        "siren_in_siret_match": siren_in_siret_match
    }


    #  TVA
    if document_type == "facture":
        tva = re.search(r"\bFR\s?\d{2}\s?\d{9}\b", text, re.IGNORECASE)

        tva_value = None
        tva_conf = None
        siren_in_tva = None
        siren_match = None
        is_valid_tva = False
        missing = True

        if tva:
            missing = False
            tva_value = tva.group().replace(" ", "")
            tva_value = tva_value.upper().replace(" ", "")
            tva_value = tva_value.replace("O", "0")

            scores = []

            for item in ocr_data:
                if item["text"] in tva_value:
                    scores.append(item["confidence"])

            tva_conf = sum(scores) / len(scores) if scores else None

            # EXTRACTION SIREN DE LA TVA
            match_tva = re.match(r"^FR(\d{2})(\d{9})$", tva_value)

            if match_tva:
                tva_key = int(match_tva.group(1))
                siren_in_tva = match_tva.group(2)

                # VALIDATION CLÉ TVA
                try:
                    expected_key = (12 + 3 * (int(siren_in_tva) % 97)) % 97
                    is_valid_tva = (tva_key == expected_key)
                except:
                    is_valid_tva = False

            # RÉCUP SIREN DE RÉFÉRENCE
            siren_ref = None

            if "siren" in extracted_data and extracted_data["siren"]["value"]:
                siren_ref = extracted_data["siren"]["value"]

            elif "siret" in extracted_data and extracted_data["siret"]["value"]:
                siren_ref = extracted_data["siret"]["value"][:9]

            if siren_in_tva and siren_ref:
                siren_match = (siren_in_tva == siren_ref)

        #  TOUJOURS retourner la TVA même si absente ou invalide
        extracted_data["tva"] = {
            "value": tva_value,
            "valid": is_valid_tva,
            "confidence": tva_conf,
            "siren_in_tva": siren_in_tva,
            "siren_match": siren_match
        }


    # NOM ENTREPRISE

    # extraction du texte
    lines = [item["text"] for item in ocr_data]

    company_value = None

    # récupérer l'élément suivant société ou vendeur
    ADDRESS_KEYWORDS = [
    "rue", "avenue", "av", "boulevard", "bd",
    "route", "chemin", "impasse",
    "place", "allée", "piste", "esp"
    ]
    
    for i, line in enumerate(lines):

        if re.search(r"n[o0]m$", line.strip(), re.IGNORECASE):
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()

            if next_line:
                company_value = next_line
                break

        if "société" in line.lower() or "vendeur" in line.lower():

            company_parts = []
            for j in range(1, 4):
                if i + j < len(lines):

                    next_line = lines[i + j].strip()

                    # stop si uniquement chiffres
                    if re.match(r"^\d+$", next_line):
                        break

                    # couper si code postal présent
                    if re.search(r"\b\d{5}\b", next_line):
                        next_line = re.split(r"\b\d{5}\b", next_line)[0]

                    # stop si mots parasites
                    if next_line.lower() in ["siret", "tva", "rcs"]:
                        break
                    
                    # nettoyage 
                    next_line = re.split(r"\b(SIRET|TVA|RCS)\b", next_line, flags=re.IGNORECASE)[0]


                    # STOP si adresse détectée
                    if any(word in next_line.lower() for word in ADDRESS_KEYWORDS):
                        break

                    # nettoyer
                    next_line = next_line.strip(" ,;")

                    # stop si ligne vide 
                    if not next_line:
                        break

                    company_parts.append(next_line)

            if company_parts:
                company_value = " ".join(company_parts)

            break

    # fallback regex
    if not company_value:
        match = re.search(
            r"(?:vendeur|soc[i1]e[t7][eé])\s+([a-zA-Z][a-zA-Z\s\-]+)",
            full_text,
            re.IGNORECASE
        )
        if match:
            company_value = match.group(1).strip()

    # confiance
    if company_value:

        scores = []

        for item in ocr_data:
            if item["text"].lower() in company_value.lower():
                scores.append(item["confidence"])

        company_conf = sum(scores) / len(scores) if scores else None

    # extraction des données
        extracted_data["entreprise"] = {
            "value": company_value,
            "confidence": company_conf,
            "valid": True,
            "missing": False
        }
    else:
        extracted_data["entreprise"] = {
            "value": None,
            "confidence": None,
            "valid": False,
            "missing": True
        }

    # MONTANTS (HT / TTC)
    if document_type == "facture" or document_type == "devis":
        text = text.replace("hi", "ht")  # OCR lit mal HT
        text = re.sub(r"\s*\.\s*", ".", text)  # corrige les espaces entre les .
        text = text.replace("O", "0").replace("o", "0")  # OCR chiffres


        def clean_amount(text):
            text = text.replace("O", "0").replace("o", "0")
            text = text.replace(",", ".")
            text = text.replace(" ", "")
            text = text.replace("€", "").replace("EUR", "")
            return text

        def extract_amount(pattern, label):

            match = re.search(pattern, text, re.IGNORECASE)

            if match:
                raw_value = match.group(1)

                value = clean_amount(raw_value)

                # vérifier si le montant est positif
                try:
                    numeric_value = float(value)
                    is_valid_amount = numeric_value >= 0
                except:
                    is_valid_amount = False

                # confidence
                scores = []
                for item in ocr_data:
                    if any(part in item["text"] for part in [raw_value]):
                        scores.append(item["confidence"])

                conf = sum(scores) / len(scores) if scores else None

                extracted_data[label.lower().replace(" ", "_")] = {
                    "value": value,
                    "valid": is_valid_amount,
                    "confidence": conf,
                    "missing": False
                }
            else:
                extracted_data[label.lower().replace(" ", "_")] = {
                    "value": None,
                    "valid": False,
                    "confidence": None,
                    "missing": True
                }

        # TOTAL HT 
        extract_amount(
            r"(?:total\s*)?h[i1t][\.\s]*t?[^0-9-]*(-?\d+[.,]\d{2})",
            "Total HT"
        )

        # TOTAL TTC
        extract_amount(
            r"(?:total\s*)?t[\.\s]*t[\.\s]*c[^0-9-]*(-?\d+[.,]\d{2})",
            "Total TTC"
        )

    # Affichage des champs manquants
    missing_fields = validate_document(extracted_data)

    extracted_data["missing_fields"] = missing_fields

    # CALCUL CONFIANCE DES CHAMPS EXTRAITS

    field_confidences = []

    for field in extracted_data.values():

        if isinstance(field, dict) and field.get("confidence") is not None:
            field_confidences.append(field["confidence"])

    if field_confidences:
        extracted_confidence = sum(field_confidences) / len(field_confidences)
    else:
        extracted_confidence = None

    extracted_data["confidence_fields"] = extracted_confidence


    # RÉSULTAT 
    all_results.append({
        "file": file_path,
        "data": extracted_data
    })


    #  RÉSULTAT JSON

    json_data = json.dumps(all_results, indent=2, ensure_ascii=False)

    print(json_data)
    return all_results[0]["data"] 