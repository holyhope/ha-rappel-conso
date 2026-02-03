"""Constants for the Rappel Conso integration."""

DOMAIN = "rappel_conso"
NAME = "Rappel Conso"

# API Configuration
API_BASE_URL = "https://data.economie.gouv.fr/api/explore/v2.1"
API_DATASET = "rappelconso-v2-gtin-espaces"
API_ENDPOINT = f"{API_BASE_URL}/catalog/datasets/{API_DATASET}/records"

# Update configuration
DEFAULT_SCAN_INTERVAL = 3600  # 1 hour in seconds
FETCH_LIMIT = 100  # Number of records to fetch per API call
MAX_RECENT_RECALLS = 50  # Maximum number of recalls to keep in sensor attributes
MAX_CACHE_SIZE = 1000  # Maximum recall IDs to keep in cache

# Sensor configuration
SENSOR_NAME = "Rappel Conso"
SENSOR_ICON = "mdi:alert-circle"
ATTRIBUTION = "Data from data.gouv.fr - RappelConso"

# API parameters
API_ORDER_BY = "date_publication DESC"
API_LIMIT_PARAM = "limit"
API_OFFSET_PARAM = "offset"
API_ORDER_PARAM = "order_by"

# Service configuration
SERVICE_SEARCH_RECALLS = "search_recalls"

# Service parameters
ATTR_PRODUCT_NAMES = "product_names"
ATTR_BRANDS = "brands"
ATTR_CATEGORIES = "categories"
ATTR_KEYWORDS = "keywords"
ATTR_LIMIT = "limit"
