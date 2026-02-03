# Rappel Conso

Monitor French product recalls (Rappel Conso) directly in Home Assistant.

## What This Integration Does

- Fetches product recall data from the official French government API
- Creates a sensor with all recall information
- Updates hourly with new recalls
- Provides flexible filtering through Home Assistant templates

## Quick Start

After installation:

1. Add the integration (no configuration needed!)
2. Check the `sensor.rappel_conso` entity
3. Create template sensors to filter by category or brand
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
