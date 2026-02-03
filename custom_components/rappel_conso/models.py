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
    identification_produits: str | None = None
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


class APIResponse(BaseModel):
    """Represent the API response structure."""

    total_count: int
    results: list[RecallData] = Field(default_factory=list)

    def get_recall_ids(self) -> set[int]:
        """Get set of recall IDs from results."""
        return {recall.id for recall in self.results}
