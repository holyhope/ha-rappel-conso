# Quick Start Guide

## Installation

### Via HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the 3 dots menu (⋮) in the top right
4. Select "Custom repositories"
5. Add repository URL: `https://github.com/holyhope/ha-rappel-conso`
6. Select category: "Integration"
7. Click "Add"
8. Find "Rappel Conso" in HACS and click "Download"
9. Restart Home Assistant
10. Go to Settings → Devices & Services → Add Integration
11. Search for "Rappel Conso" and click to add

### Manual Installation

1. Copy the `custom_components/rappel_conso` folder to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Add Integration
4. Search for "Rappel Conso" and click to add

## First Steps After Installation

### Check the Sensor

Go to Developer Tools → States and look for `sensor.rappel_conso`

You should see:
- **State**: Total number of recalls (e.g., "16341")
- **Attributes**:
  - `last_update`: When data was last fetched
  - `new_recalls_count`: New recalls since last check
  - `recent_recalls`: Array of 50 most recent recalls

### Create Your First Template Sensor

Add to your `configuration.yaml`:

```yaml
template:
  - sensor:
      - name: "Food Recalls"
        state: >
          {{ state_attr('sensor.rappel_conso', 'recent_recalls')
             | selectattr('categorie_produit', 'eq', 'alimentation')
             | list | count }}
```

### Create Your First Automation

Using events (recommended):

```yaml
automation:
  - alias: "Notify on New Recall"
    trigger:
      - platform: event
        event_type: rappel_conso_new_recall
    action:
      - service: persistent_notification.create
        data:
          title: "⚠️ Nouveau rappel de produit"
          message: >
            {{ trigger.event.data.product_name }} ({{ trigger.event.data.brand }})
            Category: {{ trigger.event.data.category }}
```

Filter by category:

```yaml
automation:
  - alias: "Notify on Food Recall"
    trigger:
      - platform: event
        event_type: rappel_conso_new_recall
    condition:
      - condition: template
        value_template: "{{ trigger.event.data.category == 'alimentation' }}"
    action:
      - service: notify.mobile_app
        data:
          title: "🍽️ Rappel Alimentaire"
          message: >
            {{ trigger.event.data.product_name }}
            Risks: {{ trigger.event.data.risks }}
            [View recall]({{ trigger.event.data.recall_link }})
```

Filter by brand:

```yaml
automation:
  - alias: "Carrefour Recalls"
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
          title: "⚠️ Rappel Carrefour"
          message: "{{ trigger.event.data.product_name }}"
```

## Event Data

When a new recall is detected, the integration fires a `rappel_conso_new_recall` event with the following data:

- `recall_id`: Unique recall identifier
- `numero_fiche`: Recall sheet number
- `product_name`: Product name
- `category`: Product category (e.g., "alimentation")
- `subcategory`: Product subcategory
- `brand`: Brand name
- `publication_date`: Publication date (ISO format)
- `recall_reason`: Reason for recall
- `risks`: Risks description
- `recall_link`: Link to official recall page

Access event data in automations with: `{{ trigger.event.data.field_name }}`

## Troubleshooting

### Sensor shows "unavailable"
- Check Home Assistant logs: Settings → System → Logs
- Verify internet connection
- Test API manually: https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/rappelconso-v2-gtin-espaces/records?limit=1

### No data in attributes
- Wait for first update (up to 1 hour)
- Force update by reloading the integration
- Check logs for errors

### Templates not working
- Verify field names match API response (case-sensitive)
- Test templates in Developer Tools → Template
- Check that `recent_recalls` is not empty

## Available Fields

Both events and sensor attributes use English field names:

### Core Fields
- `recall_id` / `id`: Unique identifier
- `sheet_number`: Official recall sheet number (was: numero_fiche)
- `version_number`: Version number (was: numero_version)
- `recall_guid`: Recall GUID (was: rappel_guid)
- `product_name`: Product name (was: libelle)
- `category`: Product category (was: categorie_produit)
- `subcategory`: Product subcategory (was: sous_categorie_produit)
- `brand`: Brand name (was: marque_produit)
- `publication_date`: Publication date (was: date_publication)
- `recall_reason`: Reason for recall (was: motif_rappel)
- `risks`: Risks description (was: risques_encourus)
- `recall_link`: Link to official recall page (was: lien_vers_la_fiche_rappel)
- And many more fields (all with English names)

## Filtering Examples

### By Category
```yaml
{{ state_attr('sensor.rappel_conso', 'recent_recalls')
   | selectattr('category', 'eq', 'alimentation')
   | list }}
```

### By Brand (case-insensitive search)
```yaml
{{ state_attr('sensor.rappel_conso', 'recent_recalls')
   | selectattr('brand', 'search', 'carrefour', ignorecase=True)
   | list }}
```

### By Date (recent 7 days)
```yaml
{% set week_ago = (now() - timedelta(days=7)).isoformat() %}
{{ state_attr('sensor.rappel_conso', 'recent_recalls')
   | selectattr('publication_date', '>=', week_ago)
   | list }}
```

## Support

- GitHub Issues: https://github.com/holyhope/ha-rappel-conso/issues
- README: https://github.com/holyhope/ha-rappel-conso
