from flask import Flask
from flask_cors import CORS
from .routes import api_bp
from .services.realtokens_data import start_realtokens_updater
from API.logging.logging_config import setup_logging
from API.logging.send_telegram_alert import send_telegram_alert
from API.logging.shutdown_handler import install_signal_handlers
import logging
import json

import os
from dotenv import load_dotenv
load_dotenv()

CORS_ORIGIN_REGEX = os.getenv("CORS_ORIGIN_REGEX")

POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_READER_USER_NAME = os.getenv("POSTGRES_READER_USER_NAME")
POSTGRES_READER_USER_PASSWORD = os.getenv("POSTGRES_READER_USER_PASSWORD")
POSTGRES_DATA = [POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_READER_USER_NAME, POSTGRES_READER_USER_PASSWORD]

def create_app():
    
    # Set up logging at the start of your application and handlers
    setup_logging()
    install_signal_handlers()
    
    # Get a logger for this module
    logger = logging.getLogger(__name__)
    logger.info("Application started")
    send_telegram_alert("yam transaction report generator: Application has started")

    app = Flask(__name__)

    # CORS
    CORS(app, 
         origins=[CORS_ORIGIN_REGEX],
         methods=['GET', 'POST', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization'],
         supports_credentials=False
    )

    app.config['POSTGRES_DATA'] = POSTGRES_DATA
    app.config['REALTOKENS_API_URL'] = os.environ['REALTOKENS_API_URL']
    
    # Optional configuration (with default)
    app.config['API_PORT'] = int(os.getenv('API_PORT_INTERNAL', '5000'))

    # Maximum size of paylaod (128 KB)
    app.config["MAX_CONTENT_LENGTH"] = 128 * 1024
    
    try:
        with open('Ressources/blockchain_contracts.json', 'r') as contracts_file:
            app.config['BLOCKCHAIN_CONTRACTS'] = json.load(contracts_file)['contracts']
        logger.info("Blockchain contracts loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load blockchain contracts: {e}")
        send_telegram_alert(f"Failed to load blockchain contracts, please check blockchain_contracts.json: {e}")
        raise
    
    # Start RealTokens data service
    start_realtokens_updater(app)
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app