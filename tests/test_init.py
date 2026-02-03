"""Tests for the Rappel Conso integration."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from httpx import Response

from custom_components.rappel_conso.const import DOMAIN

pytestmark = pytest.mark.asyncio

# Mock API response data
MOCK_API_RESPONSE = {
    "total_count": 16341,
    "results": [
        {
            "id": 824,
            "numero_fiche": "2021-06-0255",
            "libelle": "glace cookie dough",
            "categorie_produit": "alimentation",
            "sous_categorie_produit": "lait et produits laitiers",
            "marque_produit": "carrefour sensation",
            "date_publication": "2021-06-14T10:24:15+00:00",
            "motif_rappel": (
                "teneur en oxyde d'éthylène dépassant les limites autorisées"
            ),
            "risques_encourus": "dépassement des limites autorisées de pesticides",
            "lien_vers_la_fiche_rappel": "https://rappel.conso.gouv.fr/fiche-rappel/824/interne",
        }
    ],
}


@pytest.fixture
def mock_httpx_client():
    """Mock httpx client."""
    with patch("custom_components.rappel_conso.coordinator.httpx.AsyncClient") as mock:
        client = AsyncMock()
        response = AsyncMock(spec=Response)
        response.json.return_value = MOCK_API_RESPONSE
        response.raise_for_status = AsyncMock()
        client.get.return_value = response
        client.aclose = AsyncMock()
        mock.return_value = client
        yield client


@pytest.fixture
def mock_config_entry(hass: HomeAssistant):
    """Mock config entry."""
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Rappel Conso",
        data={},
        options={},
        unique_id=DOMAIN,
    )
    entry.add_to_hass(hass)
    return entry


async def test_setup_entry(hass: HomeAssistant, mock_config_entry, mock_httpx_client):
    """Test setting up the integration."""
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state == ConfigEntryState.LOADED
    assert DOMAIN in hass.data


async def test_unload_entry(hass: HomeAssistant, mock_config_entry, mock_httpx_client):
    """Test unloading the integration."""
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state == ConfigEntryState.NOT_LOADED
    # Check that domain coordinator was cleaned up
    assert mock_config_entry.entry_id not in hass.data.get(DOMAIN, {})


async def test_sensor_state(hass: HomeAssistant, mock_config_entry, mock_httpx_client):
    """Test sensor state."""
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("sensor.rappel_conso")
    assert state is not None
    assert state.state == "16341"
    # Check for new_recalls_count (may be 0 or 1 depending on coordinator state)
    assert "new_recalls_count" in state.attributes
    assert len(state.attributes["recent_recalls"]) == 1
    assert state.attributes["recent_recalls"][0]["libelle"] == "glace cookie dough"
