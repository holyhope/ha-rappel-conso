"""Tests for the config flow."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from httpx import HTTPError, Response

from custom_components.rappel_conso.const import DOMAIN

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_httpx_get():
    """Mock httpx get method."""
    with patch("httpx.AsyncClient.get") as mock:
        response = AsyncMock(spec=Response)
        response.json.return_value = {"total_count": 16341, "results": []}
        response.raise_for_status = AsyncMock()
        mock.return_value = response
        yield mock


async def test_user_flow_success(hass: HomeAssistant, mock_httpx_get):
    """Test successful user flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={}
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Rappel Conso"
    assert result["data"] == {}


async def test_user_flow_connection_error(hass: HomeAssistant):
    """Test connection error during user flow."""
    with patch("httpx.AsyncClient.get", side_effect=HTTPError("Connection failed")):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input={}
        )

        assert result["type"] == FlowResultType.FORM
        assert result["errors"] == {"base": "cannot_connect"}


async def test_user_flow_invalid_response(hass: HomeAssistant):
    """Test invalid response during user flow."""
    with patch("httpx.AsyncClient.get") as mock:
        response = AsyncMock(spec=Response)
        response.json.return_value = {"invalid": "response"}
        response.raise_for_status = AsyncMock()
        mock.return_value = response

        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input={}
        )

        assert result["type"] == FlowResultType.FORM
        assert result["errors"] == {"base": "invalid_response"}


async def test_user_flow_already_configured(hass: HomeAssistant, mock_httpx_get):
    """Test flow when already configured."""
    # Set up first entry
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    await hass.config_entries.flow.async_configure(result["flow_id"], user_input={})

    # Try to set up again
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={}
    )

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "already_configured"
