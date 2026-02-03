"""Data update coordinator for Rappel Conso."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

import httpx
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
    API_ENDPOINT,
    API_LIMIT_PARAM,
    API_OFFSET_PARAM,
    API_ORDER_BY,
    API_ORDER_PARAM,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    FETCH_LIMIT,
    MAX_CACHE_SIZE,
    MAX_RECENT_RECALLS,
)
from .models import APIResponse

_LOGGER = logging.getLogger(__name__)


class RappelConsoCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to fetch Rappel Conso data."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self._known_recall_ids: set[int] = set()
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=30.0,
                follow_redirects=True,
            )
        return self._client

    def _fire_new_recall_events(
        self, all_recalls: list[dict[str, Any]], new_recall_ids: set[int]
    ) -> None:
        """Fire events for each new recall."""
        for recall in all_recalls:
            if recall.get("id") in new_recall_ids:
                self.hass.bus.async_fire(
                    "rappel_conso_new_recall",
                    {
                        "recall_id": recall.get("id"),
                        "sheet_number": recall.get("sheet_number"),
                        "version_number": recall.get("version_number"),
                        "recall_guid": recall.get("recall_guid"),
                        "product_name": recall.get("product_name"),
                        "category": recall.get("category"),
                        "subcategory": recall.get("subcategory"),
                        "brand": recall.get("brand"),
                        "publication_date": recall.get("publication_date"),
                        "recall_reason": recall.get("recall_reason"),
                        "risks": recall.get("risks"),
                        "recall_link": recall.get("recall_link"),
                    },
                )
        _LOGGER.debug("Fired %d new recall events", len(new_recall_ids))

    async def async_search_recalls(  # pylint: disable=too-many-locals,too-many-positional-arguments
        self,
        product_names: list[str] | None = None,
        brands: list[str] | None = None,
        categories: list[str] | None = None,
        keywords: list[str] | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Search for recalls matching the given criteria.

        Uses ODSQL (Opendatasoft Query Language) for the where clause.
        Documentation: https://help.opendatasoft.com/apis/ods-explore-v2/

        Args:
            product_names: List of product names to search
                (case-insensitive, partial match)
            brands: List of brand names to search
                (case-insensitive, partial match)
            categories: List of categories to search (exact match)
            keywords: List of keywords to search across all fields
                (case-insensitive, partial match)
            limit: Maximum number of results to return

        Returns:
            List of matching recalls with English field names

        Raises:
            httpx.HTTPError: If API request fails
        """
        import urllib.parse

        client = await self._get_client()

        # Build API query parameters
        params = {
            API_LIMIT_PARAM: min(limit, 1000),  # API max limit
            API_OFFSET_PARAM: 0,
            API_ORDER_PARAM: API_ORDER_BY,
        }

        # Build ODSQL where clause
        # Note: ODSQL supports SQL-like LIKE operator with wildcards (%)
        # Case-insensitive by default
        where_clauses = []

        if product_names:
            # Search in libelle field (product name)
            # Use LIKE with wildcards for partial matching
            product_conditions = " OR ".join(
                f"libelle like '%{urllib.parse.quote(name, safe='')}%'"
                for name in product_names
            )
            where_clauses.append(f"({product_conditions})")

        if brands:
            # Search in marque_produit field (brand)
            brand_conditions = " OR ".join(
                f"marque_produit like '%{urllib.parse.quote(brand, safe='')}%'"
                for brand in brands
            )
            where_clauses.append(f"({brand_conditions})")

        if categories:
            # Search in categorie_produit field (exact match)
            category_conditions = " OR ".join(
                f"categorie_produit='{urllib.parse.quote(cat, safe='')}'"
                for cat in categories
            )
            where_clauses.append(f"({category_conditions})")

        if keywords:
            # Search across multiple fields for maximum flexibility
            keyword_conditions = []
            for keyword in keywords:
                escaped_keyword = urllib.parse.quote(keyword, safe="")
                keyword_conditions.append(
                    f"(libelle like '%{escaped_keyword}%' OR "
                    f"marque_produit like '%{escaped_keyword}%' OR "
                    f"sous_categorie_produit like '%{escaped_keyword}%' OR "
                    f"motif_rappel like '%{escaped_keyword}%')"
                )
            where_clauses.append(f"({' OR '.join(keyword_conditions)})")

        # Combine all where clauses with AND
        if where_clauses:
            params["where"] = " AND ".join(where_clauses)

        _LOGGER.debug("Searching recalls with params: %s", params)

        try:
            response = await client.get(API_ENDPOINT, params=params)
            response.raise_for_status()

            data = response.json()
            api_response = APIResponse(**data)

            # Convert to English field names
            results = [recall.to_english_dict() for recall in api_response.results]

            _LOGGER.info(
                "Found %d recalls matching search criteria (total: %d)",
                len(results),
                api_response.total_count,
            )

            return results  # noqa: TRY300

        except httpx.HTTPError:
            _LOGGER.exception("Error searching recalls")
            raise

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        try:
            client = await self._get_client()

            # Fetch first page of results
            all_recalls: list[dict[str, Any]] = []
            offset = 0
            new_recall_ids: set[int] = set()
            total_count = 0

            while True:
                params = {
                    API_LIMIT_PARAM: FETCH_LIMIT,
                    API_OFFSET_PARAM: offset,
                    API_ORDER_PARAM: API_ORDER_BY,
                }

                _LOGGER.debug(
                    "Fetching recalls: offset=%d, limit=%d", offset, FETCH_LIMIT
                )

                response = await client.get(API_ENDPOINT, params=params)
                response.raise_for_status()

                data = response.json()
                api_response = APIResponse(**data)
                total_count = api_response.total_count

                if not api_response.results:
                    break

                # Track new recalls (not in our cache)
                current_page_ids = api_response.get_recall_ids()
                new_in_page = current_page_ids - self._known_recall_ids
                new_recall_ids.update(new_in_page)

                # Add recalls to our collection
                all_recalls.extend(
                    recall.to_english_dict() for recall in api_response.results
                )

                # Stop if we've collected enough or if most recalls are known
                if (
                    len(all_recalls) >= MAX_RECENT_RECALLS * 2
                ):  # Fetch extra to ensure we get all new ones
                    break

                # If less than 20% are new, we've probably got all recent ones
                if len(new_in_page) < FETCH_LIMIT * 0.2:
                    _LOGGER.debug("Most recalls already known, stopping pagination")
                    break

                offset += FETCH_LIMIT

            # Update our known IDs cache
            if all_recalls:
                self._known_recall_ids.update(
                    recall["id"] for recall in all_recalls if "id" in recall
                )
                # Keep cache size reasonable (last MAX_CACHE_SIZE IDs)
                if len(self._known_recall_ids) > MAX_CACHE_SIZE:
                    # Remove oldest IDs (smaller numbers typically older)
                    sorted_ids = sorted(self._known_recall_ids)
                    self._known_recall_ids = set(sorted_ids[-MAX_CACHE_SIZE:])

            # Keep only most recent recalls for sensor attributes
            recent_recalls = all_recalls[:MAX_RECENT_RECALLS]

            _LOGGER.info(
                "Fetched %d recalls (%d new) - Total in dataset: %d",
                len(all_recalls),
                len(new_recall_ids),
                total_count,
            )

            # Fire events for each new recall
            if new_recall_ids:
                self._fire_new_recall_events(all_recalls, new_recall_ids)

            return {
                "total_count": total_count,
                "recent_recalls": recent_recalls,
                "new_recalls_count": len(new_recall_ids),
                "last_update": dt_util.utcnow().isoformat(),
            }

        except httpx.HTTPStatusError as err:
            raise UpdateFailed(
                f"HTTP error occurred: {err.response.status_code}"
            ) from err
        except httpx.RequestError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        except Exception as err:
            _LOGGER.exception("Unexpected error fetching recall data")
            raise UpdateFailed(f"Unexpected error: {err}") from err

    async def async_shutdown(self) -> None:
        """Shutdown coordinator and cleanup resources."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
