#!/usr/bin/env python3

## For DEV mode only! NOT TO BE USED IN PRODUCTION ###

import json
import sys
import os
from pdf_generator_module.api.app import create_app

if __name__ == '__main__':
    try:
        # Load configuration to get the port
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
        
        # Get port from config
        port = config.get('api_port', 5000)  # Default to 5000 if not found
        
        # Create the Flask app
        app = create_app()
        
        # Run the app
        print(f"Starting API server on port {port}...")
        app.run(host='0.0.0.0', port=port, debug=True)
        
    except FileNotFoundError:
        print("Error: config.json file not found!")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: Invalid JSON in config.json!")
        sys.exit(1)
    except KeyError as e:
        print(f"Error: Missing configuration key: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)