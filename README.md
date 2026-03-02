# Rappel Conso - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/holyhope/ha-rappel-conso.svg)](https://github.com/holyhope/ha-rappel-conso/releases)
[![License](https://img.shields.io/github/license/holyhope/ha-rappel-conso.svg)](LICENSE)

A Home Assistant custom integration that monitors French product recalls (Rappel Conso) from the official data.gouv.fr API.

## Features

- 🔔 **Real-time monitoring** of French product recalls
- 🎯 **Flexible filtering** via events and the `search_recalls` service
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

## Events

### rappel_conso_new_recall

Fired when a new product recall is detected (once per recall).

**Event Data:**
- `recall_id`: Unique recall identifier
- `sheet_number`: Recall sheet number
- `version_number`: Version number
- `recall_guid`: Recall GUID
- `product_name`: Product name
- `category`: Product category (e.g., "alimentation")
- `subcategory`: Product subcategory
- `brand`: Brand name
- `publication_date`: Publication date (ISO format)
- `recall_reason`: Reason for recall
- `risks`: Risks description
- `recall_link`: Link to official recall page

**Examples:**
- Filter by category: `{{ trigger.event.data.category == 'alimentation' }}`
- Filter by brand: `{{ 'carrefour' in trigger.event.data.brand | lower }}`
- Access product name: `{{ trigger.event.data.product_name }}`
- Access recall link: `{{ trigger.event.data.recall_link }}`

## Usage Examples

### Event-Based Automation (Recommended)

Get notified immediately when any new recall is detected:

```yaml
automation:
  - alias: "New Product Recall Alert"
    trigger:
      - platform: event
        event_type: rappel_conso_new_recall
    action:
      - service: notify.mobile_app
        data:
          title: "⚠️ New Product Recall"
          message: >
            {{ trigger.event.data.product_name }} ({{ trigger.event.data.brand }})
            Category: {{ trigger.event.data.category }}
            [View Details]({{ trigger.event.data.recall_link }})
```

### Filter by Category

Get notified only for food recalls:

```yaml
automation:
  - alias: "Food Recall Alert"
    trigger:
      - platform: event
        event_type: rappel_conso_new_recall
    condition:
      - condition: template
        value_template: "{{ trigger.event.data.category == 'alimentation' }}"
    action:
      - service: notify.mobile_app
        data:
          title: "🍽️ Food Product Recall"
          message: >
            {{ trigger.event.data.product_name }}
            Reason: {{ trigger.event.data.recall_reason }}
            Risks: {{ trigger.event.data.risks }}
```

### Filter by Brand

Get notified when a specific brand has a recall:

```yaml
automation:
  - alias: "Carrefour Recall Alert"
    trigger:
      - platform: event
        event_type: rappel_conso_new_recall
    condition:
      - condition: template
        value_template: >
          {{ 'carrefour' in trigger.event.data.brand | lower }}
    action:
      - service: notify.mobile_app
        data:
          title: "⚠️ Carrefour Product Recall"
          message: "{{ trigger.event.data.product_name }}"
```

## Automation Actions

### rappel_conso.search_recalls

Search for product recalls based on various criteria. Returns a list of matching recalls that can be used in automation conditions or actions.

**Parameters:**
- `product_names` (optional): List of product names to search (case-insensitive, partial match)
- `brands` (optional): List of brand names to search (case-insensitive, partial match)
- `categories` (optional): List of categories to search (e.g., "alimentation", "cosmetique")
- `keywords` (optional): List of keywords to search across all fields
- `limit` (optional): Maximum number of results (default: 100, max: 1000)

**Returns:**
- `recalls`: List of matching recall objects with English field names
- `count`: Number of recalls found

**Example: Check if products in shopping list are recalled**

```yaml
automation:
  - alias: "Check Shopping List for Recalls"
    triggers:
      - trigger: time
        at: "08:00:00"
    actions:
      - action: rappel_conso.search_recalls
        data:
          product_names:
            - "{{ states('input_text.shopping_item_1') }}"
            - "{{ states('input_text.shopping_item_2') }}"
          limit: 50
        response_variable: search_result
      - if: "{{ search_result.count > 0 }}"
        then:
          - action: notify.notify
            data:
              title: "Product Recall Alert!"
              message: >
                Found {{ search_result.count }} recalled products in your shopping list:
                {% for recall in search_result.recalls %}
                - {{ recall.product_name }} ({{ recall.brand }})
                {% endfor %}
```

**Example: Monitor specific brands**

```yaml
automation:
  - alias: "Check Carrefour Products Daily"
    triggers:
      - trigger: time
        at: "09:00:00"
    actions:
      - action: rappel_conso.search_recalls
        data:
          brands: ["carrefour"]
          categories: ["alimentation"]
          limit: 100
        response_variable: recalls
      - action: persistent_notification.create
        data:
          title: "Carrefour Food Recalls"
          message: "Found {{ recalls.count }} food recalls from Carrefour"
```

**Example: Search by keywords**

```yaml
automation:
  - alias: "Search for Chocolate Products"
    triggers:
      - trigger: state
        entity_id: input_boolean.check_chocolate_recalls
        to: "on"
    actions:
      - action: rappel_conso.search_recalls
        data:
          keywords: ["chocolate", "chocolat"]
          categories: ["alimentation"]
        response_variable: results
      - action: notify.notify
        data:
          message: "Found {{ results.count }} chocolate-related recalls"
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

### Integration or API issues

- Check your internet connection
- Verify the API is accessible: https://data.economie.gouv.fr
- Check Home Assistant logs for error messages

### No new recalls detected

- The dataset updates hourly, be patient
- Recalls are only added when genuinely new products are recalled
- Check Home Assistant logs to confirm the coordinator is fetching data

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
