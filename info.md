# Rappel Conso

Monitor French product recalls (Rappel Conso) directly in Home Assistant.

## What This Integration Does

- Fetches product recall data from the official French government API
- Fires events for new recalls and provides a search service for product recalls
- Updates hourly with new recalls
- Provides flexible filtering via events and the search service

## Quick Start

After installation:

1. Add the integration (no configuration needed!)
2. Use the `rappel_conso.search_recalls` service or listen for `rappel_conso_new_recall` events
3. Use the search service or event triggers to filter by category or brand
4. Set up automations for notifications

## Example Uses

- Monitor food recalls for specific brands
- Track recalls in your region
- Get notified about dangerous products
- Display recent recalls on your dashboard

## Data Source

Official French government data from rappel.conso.gouv.fr, updated hourly.

## Support

[GitHub Repository](https://github.com/holyhope/ha-rappel-conso) | [Issues](https://github.com/holyhope/ha-rappel-conso/issues)
