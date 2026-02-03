# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-30

### Added
- Initial release
- Single sensor (`sensor.rappel_conso`) with all product recall data
- Automatic hourly updates from data.gouv.fr API (RappelConso V2 dataset)
- Zero-configuration setup (one-click installation)
- French and English translations
- HACS compatibility
- Comprehensive documentation:
  - README with usage examples
  - QUICKSTART guide
  - CONTRIBUTING guide for developers
  - Template sensor examples for filtering
  - Automation examples for notifications
- Complete code quality pipeline:
  - Pre-commit hooks (Ruff, PyLint)
  - GitHub Actions CI/CD
  - Automated testing with pytest
  - Code coverage reporting

### BREAKING CHANGES

- **English field names everywhere**: ALL fields now use English names (product_name, category, brand, sheet_number, version_number, recall_guid, etc.) instead of French API names
- **Events changed**: Event field names updated to fully English:
  - `numero_fiche` → `sheet_number`
  - Event now includes `version_number` and `recall_guid` fields
- **English UI by default**: Integration UI text is now in English by default with full French translations available
- **Migration required**: Users must update:
  - Template sensors referencing sensor attributes
  - Automations listening to events
  - Key field name changes:
    - `libelle` → `product_name`
    - `categorie_produit` → `category`
    - `marque_produit` → `brand`
    - `numero_fiche` → `sheet_number`
    - `numero_version` → `version_number`
    - `rappel_guid` → `recall_guid`
  - See full field mapping in MIGRATION.md

### Features
- **Zero-configuration**: No user input required, works out of the box
- **Real-time monitoring**: Tracks 50 most recent recalls with all fields
- **Event-based automations**: Fires `rappel_conso_new_recall` events for granular control with English field names
- **Change detection**: Automatically tracks new recalls since last check
- **Efficient API usage**: Pagination and smart caching (max 1000 recall IDs)
- **Flexible filtering**: Users create template sensors for custom filtering or use event conditions
- **Comprehensive data**: All recall fields exposed as sensor attributes including:
  - Product information (name, brand, category)
  - Recall details (reason, risks, date)
  - Official links and documentation
- **Proper error handling**: Graceful degradation on API errors
- **Detailed logging**: Debug-friendly error messages

### Technical Details
- Update interval: 3600 seconds (1 hour)
- Max recalls in attributes: 50 most recent
- API endpoint: data.economie.gouv.fr RappelConso V2
- Dependencies: httpx >= 0.27.0, pydantic >= 2.0.0
- Python: 3.13+ supported
- Test coverage: 9 passing tests (including event firing and field mapping validation)

[1.0.0]: https://github.com/holyhope/ha-rappel-conso/releases/tag/v1.0.0
