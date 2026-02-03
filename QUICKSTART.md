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

```yaml
automation:
  - alias: "Notify on New Recall"
    trigger:
      - platform: state
        entity_id: sensor.rappel_conso
        attribute: new_recalls_count
    condition:
      - "{{ trigger.to_state.attributes.new_recalls_count > 0 }}"
    action:
      - service: persistent_notification.create
        data:
          title: "⚠️ Nouveaux rappels de produits"
          message: >
            {{ trigger.to_state.attributes.new_recalls_count }} nouveau(x) rappel(s) détecté(s).
```

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

Each recall in `recent_recalls` includes:
- `id`, `numero_fiche`, `libelle` (product name)
- `categorie_produit`, `sous_categorie_produit`
- `marque_produit` (brand)
- `motif_rappel` (recall reason)
- `risques_encourus` (risks)
- `date_publication` (publication date)
- `lien_vers_la_fiche_rappel` (link to official page)
- And many more...

## Filtering Examples

### By Category
```yaml
{{ state_attr('sensor.rappel_conso', 'recent_recalls')
   | selectattr('categorie_produit', 'eq', 'alimentation')
   | list }}
```

### By Brand (case-insensitive search)
```yaml
{{ state_attr('sensor.rappel_conso', 'recent_recalls')
   | selectattr('marque_produit', 'search', 'carrefour', ignorecase=True)
   | list }}
```

### By Date (recent 7 days)
```yaml
{% set week_ago = (now() - timedelta(days=7)).isoformat() %}
{{ state_attr('sensor.rappel_conso', 'recent_recalls')
   | selectattr('date_publication', '>=', week_ago)
   | list }}
```

## Support

- GitHub Issues: https://github.com/holyhope/ha-rappel-conso/issues
- README: https://github.com/holyhope/ha-rappel-conso
