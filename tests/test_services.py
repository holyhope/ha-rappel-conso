"""Tests for Rappel Conso service actions."""

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from httpx import Response
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.rappel_conso.const import (
    ATTR_BRANDS,
    ATTR_CATEGORIES,
    ATTR_KEYWORDS,
    ATTR_LIMIT,
    ATTR_PRODUCT_NAMES,
    DOMAIN,
    SERVICE_SEARCH_RECALLS,
)


@pytest.fixture
async def init_integration(hass: HomeAssistant) -> ConfigEntry:
    """Set up the integration for testing."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        title="Rappel Conso",
        data={},
    )
    config_entry.add_to_hass(hass)

    # Mock httpx client like in test_init.py
    with patch(
        "custom_components.rappel_conso.coordinator.httpx.AsyncClient"
    ) as mock_client_class:
        client = AsyncMock()
        response = AsyncMock(spec=Response)
        response.json.return_value = {
            "total_count": 1,
            "results": [
                {
                    "id": 824,
                    "libelle": "glace cookie dough",
                    "categorie_produit": "alimentation",
                    "marque_produit": "carrefour sensation",
                    "numero_fiche": "2021-06-0255",
                    "numero_version": 1,
                    "rappel_guid": "0a07750e-aaba-41d7-82e5-100dcf7c9f8c",
                    "date_publication": "2021-06-14T10:24:15+00:00",
                    "motif_rappel": "test",
                    "risques_encourus": "test risks",
                    "lien_vers_la_fiche_rappel": "https://example.com",
                }
            ],
        }
        response.raise_for_status = AsyncMock()
        client.get.return_value = response
        client.aclose = AsyncMock()
        mock_client_class.return_value = client

        assert await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

    return config_entry


async def test_search_by_product_names(hass: HomeAssistant, init_integration):
    """Test searching recalls by product names."""
    # Access the coordinator from hass.data
    coordinator = hass.data[DOMAIN][init_integration.entry_id]

    search_response = {
        "total_count": 1,
        "results": [
            {
                "id": 824,
                "libelle": "glace cookie dough",
                "categorie_produit": "alimentation",
                "marque_produit": "carrefour sensation",
                "numero_fiche": "2021-06-0255",
                "numero_version": 1,
                "rappel_guid": "0a07750e-aaba-41d7-82e5-100dcf7c9f8c",
                "date_publication": "2021-06-14T10:24:15+00:00",
                "motif_rappel": "test",
                "risques_encourus": "test risks",
                "lien_vers_la_fiche_rappel": "https://example.com",
            }
        ],
    }

    # Get the client and patch its get method
    client = await coordinator._get_client()
    response = AsyncMock(spec=Response)
    response.json.return_value = search_response
    response.raise_for_status = AsyncMock()

    with patch.object(client, "get", return_value=response):
        response_data = await hass.services.async_call(
            DOMAIN,
            SERVICE_SEARCH_RECALLS,
            {ATTR_PRODUCT_NAMES: ["cookie"]},
            blocking=True,
            return_response=True,
        )

    assert response_data["count"] == 1
    assert len(response_data["recalls"]) == 1
    assert response_data["recalls"][0]["product_name"] == "glace cookie dough"
    assert response_data["recalls"][0]["brand"] == "carrefour sensation"


async def test_search_by_brands(hass: HomeAssistant, init_integration):
    """Test searching recalls by brands."""
    coordinator = hass.data[DOMAIN][init_integration.entry_id]

    search_response = {"total_count": 0, "results": []}

    client = await coordinator._get_client()
    response = AsyncMock(spec=Response)
    response.json.return_value = search_response
    response.raise_for_status = AsyncMock()

    with patch.object(client, "get", return_value=response):
        response_data = await hass.services.async_call(
            DOMAIN,
            SERVICE_SEARCH_RECALLS,
            {ATTR_BRANDS: ["carrefour", "lidl"]},
            blocking=True,
            return_response=True,
        )

    assert response_data["count"] == 0
    assert len(response_data["recalls"]) == 0


async def test_search_by_categories(hass: HomeAssistant, init_integration):
    """Test searching recalls by categories."""
    coordinator = hass.data[DOMAIN][init_integration.entry_id]

    search_response = {"total_count": 0, "results": []}

    client = await coordinator._get_client()
    response = AsyncMock(spec=Response)
    response.json.return_value = search_response
    response.raise_for_status = AsyncMock()

    with patch.object(client, "get", return_value=response):
        response_data = await hass.services.async_call(
            DOMAIN,
            SERVICE_SEARCH_RECALLS,
            {ATTR_CATEGORIES: ["alimentation"]},
            blocking=True,
            return_response=True,
        )

    assert response_data["count"] == 0
    assert len(response_data["recalls"]) == 0


async def test_search_by_keywords(hass: HomeAssistant, init_integration):
    """Test searching recalls by keywords."""
    coordinator = hass.data[DOMAIN][init_integration.entry_id]

    search_response = {"total_count": 0, "results": []}

    client = await coordinator._get_client()
    response = AsyncMock(spec=Response)
    response.json.return_value = search_response
    response.raise_for_status = AsyncMock()

    with patch.object(client, "get", return_value=response):
        response_data = await hass.services.async_call(
            DOMAIN,
            SERVICE_SEARCH_RECALLS,
            {ATTR_KEYWORDS: ["chocolate", "frozen"]},
            blocking=True,
            return_response=True,
        )

    assert response_data["count"] == 0
    assert len(response_data["recalls"]) == 0


async def test_search_multiple_criteria(hass: HomeAssistant, init_integration):
    """Test searching recalls with multiple criteria."""
    coordinator = hass.data[DOMAIN][init_integration.entry_id]

    search_response = {"total_count": 0, "results": []}

    client = await coordinator._get_client()
    response = AsyncMock(spec=Response)
    response.json.return_value = search_response
    response.raise_for_status = AsyncMock()

    with patch.object(client, "get", return_value=response) as mock_get:
        response_data = await hass.services.async_call(
            DOMAIN,
            SERVICE_SEARCH_RECALLS,
            {
                ATTR_PRODUCT_NAMES: ["cookie"],
                ATTR_BRANDS: ["carrefour"],
                ATTR_CATEGORIES: ["alimentation"],
                ATTR_LIMIT: 50,
            },
            blocking=True,
            return_response=True,
        )

    assert response_data["count"] == 0
    assert len(response_data["recalls"]) == 0

    # Verify the where clause was properly constructed
    call_args = mock_get.call_args
    assert call_args
    assert "params" in call_args[1]
    assert "where" in call_args[1]["params"]


async def test_search_no_criteria_error(hass: HomeAssistant, init_integration):
    """Test that searching without criteria raises an error."""
    with pytest.raises(ServiceValidationError) as exc_info:
        await hass.services.async_call(
            DOMAIN,
            SERVICE_SEARCH_RECALLS,
            {},
            blocking=True,
            return_response=True,
        )

    assert exc_info.value.translation_key == "no_search_criteria"


async def test_search_no_config_entry_error(hass: HomeAssistant):
    """Test that searching without a config entry raises an error."""
    # Don't set up the integration - service won't be registered
    # This will raise service_not_found instead
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_SEARCH_RECALLS,
            {ATTR_PRODUCT_NAMES: ["test"]},
            blocking=True,
            return_response=True,
        )


async def test_search_response_format(hass: HomeAssistant, init_integration):
    """Test that the search response has the correct format."""
    coordinator = hass.data[DOMAIN][init_integration.entry_id]

    search_response = {
        "total_count": 2,
        "results": [
            {
                "id": 1,
                "libelle": "product 1",
                "categorie_produit": "alimentation",
                "marque_produit": "brand 1",
                "numero_fiche": "2021-01-0001",
                "numero_version": 1,
                "rappel_guid": "guid-1",
                "date_publication": "2021-01-01T00:00:00+00:00",
                "motif_rappel": "reason 1",
                "risques_encourus": "risks 1",
                "lien_vers_la_fiche_rappel": "https://example.com/1",
            },
            {
                "id": 2,
                "libelle": "product 2",
                "categorie_produit": "cosmetique",
                "marque_produit": "brand 2",
                "numero_fiche": "2021-01-0002",
                "numero_version": 1,
                "rappel_guid": "guid-2",
                "date_publication": "2021-01-02T00:00:00+00:00",
                "motif_rappel": "reason 2",
                "risques_encourus": "risks 2",
                "lien_vers_la_fiche_rappel": "https://example.com/2",
            },
        ],
    }

    client = await coordinator._get_client()
    response = AsyncMock(spec=Response)
    response.json.return_value = search_response
    response.raise_for_status = AsyncMock()

    with patch.object(client, "get", return_value=response):
        response_data = await hass.services.async_call(
            DOMAIN,
            SERVICE_SEARCH_RECALLS,
            {ATTR_KEYWORDS: ["test"]},
            blocking=True,
            return_response=True,
        )

    # Verify response structure
    assert "recalls" in response_data
    assert "count" in response_data
    assert response_data["count"] == 2
    assert isinstance(response_data["recalls"], list)

    # Verify English field names
    recall = response_data["recalls"][0]
    assert "product_name" in recall
    assert "category" in recall
    assert "brand" in recall
    assert "sheet_number" in recall
    assert "version_number" in recall
    assert "recall_guid" in recall
    assert "publication_date" in recall
    assert "recall_reason" in recall
    assert "risks" in recall
    assert "recall_link" in recall

    # Verify French field names are NOT present
    assert "libelle" not in recall
    assert "categorie_produit" not in recall
    assert "marque_produit" not in recall
    assert "numero_fiche" not in recall
