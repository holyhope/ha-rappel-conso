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

### Verify setup

- In **Settings → Devices & Services**, confirm the Rappel Conso integration is loaded.
- Use **Developer Tools → Services** to call `rappel_conso.search_recalls` (e.g. with `product_names: ["test"]`) or listen for `rappel_conso_new_recall` events.

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
- `sheet_number`: Recall sheet number
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

### Integration or API issues
- Check Home Assistant logs: Settings → System → Logs
- Verify internet connection
- Test API manually: https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/rappelconso-v2-gtin-espaces/records?limit=1

### No new recalls or search returns nothing
- Wait for first coordinator update (up to 1 hour) if you rely on events
- Reload the integration to force a refresh
- Check logs for errors

## Available Fields

Events and the `search_recalls` response use English field names:

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

## Filtering with search_recalls

Use the `rappel_conso.search_recalls` service to filter by category, brand, or keywords. See the "Search Recalls Action" section below for parameters and examples. In automations, filter event data with conditions (e.g. `trigger.event.data.category == 'alimentation'`).

## Support

- GitHub Issues: https://github.com/holyhope/ha-rappel-conso/issues
- README: https://github.com/holyhope/ha-rappel-conso

## Search Recalls Action

### Quick Example

Search for recalls based on product names, brands, categories, or keywords:

```yaml
automation:
  - alias: "Check My Products for Recalls"
    triggers:
      - trigger: time
        at: "09:00:00"
    actions:
      - action: rappel_conso.search_recalls
        data:
          product_names: ["chocolate", "milk"]
          brands: ["carrefour"]
          limit: 50
        response_variable: results
      - if: "{{ results.count > 0 }}"
        then:
          - action: notify.notify
            data:
              message: "Found {{ results.count }} recalls!"
```

### Search Parameters

- `product_names`: List of product names (partial match, case-insensitive)
- `brands`: List of brand names (partial match, case-insensitive)
- `categories`: List of categories (exact match: "alimentation", "cosmetique", etc.)
- `keywords`: List of keywords to search across all fields
- `limit`: Maximum results (default: 100, max: 1000)

### Response Format

The action returns:
- `recalls`: List of recall objects with all fields
- `count`: Number of results found

### More Examples

**Search by keywords:**
```yaml
action: rappel_conso.search_recalls
data:
  keywords: ["chocolate", "peanut"]
  categories: ["alimentation"]
response_variable: results
```

**Check shopping list:**
```yaml
action: rappel_conso.search_recalls
data:
  product_names:
    - "{{ states('input_text.item_1') }}"
    - "{{ states('input_text.item_2') }}"
response_variable: shopping_recalls
```

**Monitor specific brand:**
```yaml
action: rappel_conso.search_recalls
data:
  brands: ["lidl"]
  categories: ["alimentation"]
  limit: 100
response_variable: brand_recalls
```
