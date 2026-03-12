#!/usr/bin/env python3

## For DEV mode only! NOT TO BE USED IN PRODUCTION ###

import sys
from API.core.app import create_app

import os
from dotenv import load_dotenv
load_dotenv()

if __name__ == '__main__':
    try:
        # Get port from config
        port = int(os.getenv('API_PORT_INTERNAL', '5000'))
        
        # Create the Flask app
        app = create_app()
        
        # Run the app
        print(f"Starting API server on port {port}...")
        app.run(host='0.0.0.0', port=port, debug=True)
        
    except KeyError as e:
        print(f"Error: Missing configuration key: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)