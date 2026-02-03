"""Data models for the Rappel Conso integration."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RecallData(BaseModel):
    """Represent a product recall."""

    model_config = ConfigDict(extra="allow")  # Allow additional fields from API

    id: int
    numero_fiche: str | None = None
    numero_version: int | None = None
    nature_juridique_rappel: str | None = None
    categorie_produit: str | None = None
    sous_categorie_produit: str | None = None
    marque_produit: str | None = None
    modeles_ou_references: str | None = None
    identification_produits: list[str] | None = None
    conditionnements: str | None = None
    date_debut_commercialisation: str | None = None
    date_date_fin_commercialisation: str | None = None
    temperature_conservation: str | None = None
    marque_salubrite: str | None = None
    informations_complementaires: str | None = None
    zone_geographique_de_vente: str | None = None
    distributeurs: str | None = None
    motif_rappel: str | None = None
    risques_encourus: str | None = None
    preconisations_sanitaires: str | None = None
    description_complementaire_risque: str | None = None
    conduites_a_tenir_par_le_consommateur: str | None = None
    numero_contact: str | None = None
    modalites_de_compensation: str | None = None
    date_de_fin_de_la_procedure_de_rappel: str | None = None
    informations_complementaires_publiques: str | None = None
    liens_vers_les_images: str | None = None
    lien_vers_la_liste_des_produits: str | None = None
    lien_vers_la_liste_des_distributeurs: str | None = None
    lien_vers_affichette_pdf: str | None = None
    lien_vers_la_fiche_rappel: str | None = None
    rappel_guid: str | None = None
    date_publication: str | None = None
    libelle: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for Home Assistant attributes."""
        return self.model_dump(exclude_none=True)

    def to_english_dict(self) -> dict[str, Any]:
        """Convert to dictionary with English field names for Home Assistant."""
        data = self.model_dump(exclude_none=True)

        # Map ALL French field names to English (no exceptions)
        field_mapping = {
            "libelle": "product_name",
            "categorie_produit": "category",
            "sous_categorie_produit": "subcategory",
            "marque_produit": "brand",
            "date_publication": "publication_date",
            "motif_rappel": "recall_reason",
            "risques_encourus": "risks",
            "lien_vers_la_fiche_rappel": "recall_link",
            "numero_fiche": "sheet_number",
            "numero_version": "version_number",
            "rappel_guid": "recall_guid",
            "modeles_ou_references": "models_or_references",
            "identification_produits": "product_identification",
            "conditionnements": "packaging",
            "date_debut_commercialisation": "commercialization_start_date",
            "date_date_fin_commercialisation": "commercialization_end_date",
            "temperature_conservation": "storage_temperature",
            "marque_salubrite": "health_mark",
            "informations_complementaires": "additional_information",
            "zone_geographique_de_vente": "geographic_sales_area",
            "distributeurs": "distributors",
            "preconisations_sanitaires": "health_recommendations",
            "description_complementaire_risque": "additional_risk_description",
            "conduites_a_tenir_par_le_consommateur": "consumer_actions",
            "numero_contact": "contact_number",
            "modalites_de_compensation": "compensation_terms",
            "date_de_fin_de_la_procedure_de_rappel": "recall_procedure_end_date",
            "informations_complementaires_publiques": "public_additional_information",
            "liens_vers_les_images": "image_links",
            "lien_vers_la_liste_des_produits": "product_list_link",
            "lien_vers_la_liste_des_distributeurs": "distributor_list_link",
            "lien_vers_affichette_pdf": "poster_pdf_link",
            "nature_juridique_rappel": "legal_recall_nature",
        }

        english_data = {}
        for french_key, value in data.items():
            english_key = field_mapping.get(french_key, french_key)
            english_data[english_key] = value

        return english_data


class APIResponse(BaseModel):
    """Represent the API response structure."""

    total_count: int
    results: list[RecallData] = Field(default_factory=list)

    def get_recall_ids(self) -> set[int]:
        """Get set of recall IDs from results."""
        return {recall.id for recall in self.results}
