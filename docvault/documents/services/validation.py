def validate_document(doc):

    required_fields_facture = [
        "date_emission",
        "date_facture",
        "date_paiement",
        "numero_facture",
        "siret",
        "tva",
        "entreprise",
        "total_ht",
        "total_ttc"
    ]

    required_fields_devis = [
        "date_devis",
        "date_prestation",
        "entreprise",
        "siret",
        "total_ht",
        "total_ttc"
    ]

    required_fields_attestations = [
        "siren"
    ]

    missing_fields = []

    if doc["document_type"] == "facture":
        fields = required_fields_facture
    elif doc["document_type"] == "devis":
        fields = required_fields_devis
    else:
        fields = required_fields_attestations

    for field in fields:
        if field not in doc or doc[field].get("missing"):
            missing_fields.append(field)

    return missing_fields