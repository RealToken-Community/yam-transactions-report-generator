from flask import Flask
from flask_cors import CORS
from .routes import api_bp
from .services.realtokens_data import start_realtokens_updater
from pdf_generator_module.logging.logging_config import setup_logging
import logging
import json

def create_app():
    
    # Set up logging at the start of your application
    setup_logging()
    
    # Get a logger for this module
    logger = logging.getLogger(__name__)
    logger.info("Application started")

    app = Flask(__name__)

        # Enable CORS for production - Allow all origins for public API
    CORS(app, 
         origins="*",
         methods=['GET', 'POST', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization'],
         supports_credentials=False
    )
    
    # Load configuration from config.json
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
    
    # Configuration
    app.config['DB_PATH'] = config['db_path']
    app.config['API_PORT'] = config['api_port']
    app.config['REALTOKENS_API_URL'] = config['realtokens_api_url']
    
    try:
        with open('Ressources/blockchain_contracts.json', 'r') as contracts_file:
            app.config['BLOCKCHAIN_CONTRACTS'] = json.load(contracts_file)['contracts']
        logger.info("Blockchain contracts loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load blockchain contracts: {e}")
        raise
    
    # Start RealTokens data service
    start_realtokens_updater(app)
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app