import requests
import threading
import time
import logging
from eth_utils import to_checksum_address, is_address

# Get logger for this module
logger = logging.getLogger(__name__)

def fetch_realtokens(api_url):
    """Fetch RealTokens data from the API."""
    try:
        realtokens = {}
        response = requests.get(api_url)
        response.raise_for_status()
        realtokens_raw = response.json()
        
        for realtoken in realtokens_raw:
            realtoken_address = realtoken.get('gnosisContract')
            if isinstance(realtoken_address, str) and is_address(realtoken_address):
                realtokens[to_checksum_address(realtoken['gnosisContract'])] = realtoken
        
        logger.info(f"RealTokens data fetched successfully - {len(realtokens)} tokens processed")
        return realtokens
        
    except Exception as e:
        logger.error(f"Failed to fetch RealTokens data: {e}")
        return None

def start_realtokens_updater(app):
    """Start the background task to update RealTokens data every 24 hours."""
    
    logger.info("Initializing RealTokens updater service")
    
    # Get API URL from config
    api_url = app.config['REALTOKENS_API_URL']
    
    # Initial load of RealTokens
    initial_data = fetch_realtokens(api_url)
    
    if initial_data:
        app.config['REALTOKENS'] = initial_data
        logger.info("RealTokens service initialized successfully")
    else:
        logger.error("Failed to initialize RealTokens service - cannot start application")
        raise Exception("Failed to load initial RealTokens data - cannot start application without this data")
    
    def update_realtokens_periodically():
        while True:
            time.sleep(24 * 60 * 60)  # Sleep for 24 hours
            
            with app.app_context():
                new_data = fetch_realtokens(api_url)
                if new_data:
                    app.config['REALTOKENS'] = new_data
                    logger.info("RealTokens data updated successfully (24h periodic update)")
                else:
                    logger.error("Failed to update RealTokens data (24h periodic update)")
    
    # Start background thread
    update_thread = threading.Thread(target=update_realtokens_periodically, daemon=True)
    update_thread.start()