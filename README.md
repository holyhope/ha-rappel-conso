# Rappel Conso - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/holyhope/ha-rappel-conso.svg)](https://github.com/holyhope/ha-rappel-conso/releases)
[![License](https://img.shields.io/github/license/holyhope/ha-rappel-conso.svg)](LICENSE)

A Home Assistant custom integration that monitors French product recalls (Rappel Conso) from the official data.gouv.fr API.

## Features

- 🔔 **Real-time monitoring** of French product recalls
- 📊 **Single sensor** with all recall data as attributes
- 🎯 **Flexible filtering** using Home Assistant templates and automations
- 🚀 **Zero configuration** - one-click setup
- 🔄 **Hourly updates** from official government data
- 🌍 **Bilingual** - French and English support

## What is Rappel Conso?

[Rappel Conso](https://rappel.conso.gouv.fr/) is the French government's official platform for product recalls. This integration provides real-time access to recall information including:

- Food products (DGAL)
- Consumer goods (DGCCRF)
- Energy products (DGEC)
- Risk-related products (DGPR)

## Installation

### Via HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots menu → "Custom repositories"
4. Add `https://github.com/holyhope/ha-rappel-conso` as an Integration
5. Click "Install"
6. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/rappel_conso` directory to your Home Assistant `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "Rappel Conso"
4. Click to add - no configuration needed!

The integration will create a single sensor: `sensor.rappel_conso`

## Sensor Data

### Main Sensor: `sensor.rappel_conso`

**State**: Total number of recalls in the dataset

**Attributes**:
- `last_update`: Timestamp of last check
- `new_recalls_count`: Number of new recalls since last check
- `recent_recalls`: List of 50 most recent recalls with all fields
- `attribution`: Data source attribution

### Recall Fields

Each recall in `recent_recalls` contains:
- `id`: Unique recall identifier
- `numero_fiche`: Recall sheet number
- `libelle`: Product name
- `categorie_produit`: Product category (alimentation, etc.)
- `sous_categorie_produit`: Product subcategory
- `marque_produit`: Brand name
- `motif_rappel`: Reason for recall
- `risques_encourus`: Risks
- `date_publication`: Publication date
- `lien_vers_la_fiche_rappel`: Link to official recall page
- And many more fields...

## Usage Examples

### Template Sensor for Food Recalls

Create a sensor that shows only food recalls:

```yaml
template:
  - sensor:
      - name: "Rappels Alimentaires"
        unique_id: rappel_conso_alimentation
        state: >
          {% set recalls = state_attr('sensor.rappel_conso', 'recent_recalls') %}
          {% if recalls %}
            {{ recalls | selectattr('categorie_produit', 'eq', 'alimentation')
                       | list | count }}
          {% else %}
            0
          {% endif %}
        attributes:
          recalls: >
            {% set recalls = state_attr('sensor.rappel_conso', 'recent_recalls') %}
            {% if recalls %}
              {{ recalls | selectattr('categorie_produit', 'eq', 'alimentation')
                         | list }}
            {% else %}
              []
            {% endif %}
```

### Automation for Brand-Specific Alerts

Get notified when a specific brand has a recall:

```yaml
automation:
  - alias: "Alerte Rappel Carrefour"
    trigger:
      - platform: state
        entity_id: sensor.rappel_conso
        attribute: new_recalls_count
    condition:
      - condition: template
        value_template: >
          {% set recalls = state_attr('sensor.rappel_conso', 'recent_recalls') %}
          {{ recalls | selectattr('marque_produit', 'search', 'carrefour', ignorecase=True)
                     | list | count > 0 }}
    action:
      - service: notify.mobile_app
        data:
          title: "⚠️ Rappel Produit Carrefour"
          message: >
            {{ (state_attr('sensor.rappel_conso', 'recent_recalls')
                | selectattr('marque_produit', 'search', 'carrefour', ignorecase=True)
                | list | first).libelle }}
```

### Lovelace Dashboard Card

Display recalls in your dashboard:

```yaml
type: markdown
content: >
  ## 🔔 Derniers Rappels de Produits

  {% set recalls = state_attr('sensor.rappel_conso', 'recent_recalls')[:5] %}
  {% if recalls %}
    {% for recall in recalls %}
      **{{ recall.libelle }}** ({{ recall.marque_produit }})
      - Catégorie: {{ recall.categorie_produit }}
      - Publié le: {{ recall.date_publication[:10] }}
      - [Voir la fiche]({{ recall.lien_vers_la_fiche_rappel }})

    {% endfor %}
  {% else %}
    Aucun rappel récent
  {% endif %}
```

## Filtering by Category

Product categories available:
- `alimentation` - Food products
- `equipement-electrique-electronique` - Electrical equipment
- `vehicules` - Vehicles
- `jouets` - Toys
- `cosmetiques-hygiene` - Cosmetics and hygiene
- And many more...

## Data Source

This integration uses the official French government open data:
- **Dataset**: RappelConso V2
- **Source**: [data.economie.gouv.fr](https://data.economie.gouv.fr/explore/dataset/rappelconso-v2-gtin-espaces/)
- **License**: Licence Ouverte 2.0
- **Update frequency**: Hourly

## Troubleshooting

### Sensor shows "unavailable"

- Check your internet connection
- Verify the API is accessible: https://data.economie.gouv.fr
- Check Home Assistant logs for error messages

### No new recalls detected

- The dataset updates hourly, be patient
- Check the `last_update` attribute to see when last sync occurred
- Recalls are only added when genuinely new products are recalled

### Template sensors not working

- Verify the main sensor `sensor.rappel_conso` exists and has data
- Check for typos in field names (they're case-sensitive)
- Test your templates in Developer Tools → Template

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

- 🐛 [Report a bug](https://github.com/holyhope/ha-rappel-conso/issues)
- 💡 [Request a feature](https://github.com/holyhope/ha-rappel-conso/issues)
- 📖 [Read the docs](https://github.com/holyhope/ha-rappel-conso)

## License

MIT License - see [LICENSE](LICENSE) file for details

## Attribution

Data provided by the French government through:
- DGCCRF (Direction générale de la concurrence, de la consommation et de la répression des fraudes)
- DGAL (Direction générale de l'alimentation)
- DGEC (Direction générale de l'énergie et du climat)
- DGPR (Direction générale de la prévention des risques)

Available under [Licence Ouverte 2.0](https://www.etalab.gouv.fr/wp-content/uploads/2017/04/ETALAB-Licence-Ouverte-v2.0.pdf)
