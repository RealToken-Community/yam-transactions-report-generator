from flask import Blueprint, request, jsonify, current_app, send_file
from datetime import datetime
from web3 import Web3
import io
import logging
import json
from pdf_generator_module.query_db import get_accepted_offers_by_buyer_datetime, get_accepted_offers_by_seller_datetime
from pdf_generator_module.print_pdf import create_report_elements, build_pdf

# Get logger for this module
logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

@api_bp.route('/generate-report', methods=['POST'])
def generate_report():
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Log the incoming request with all parameters
        logger.info(f"Report generation requested - Parameters:\n{json.dumps(data, indent=2, default=str)}")
        
        # Validate required fields
        required_fields = ['start_date', 'end_date', 'event_type', 'user_addresses', 'display_tx_column']
        for field in required_fields:
            if field not in data:
                logger.error(f"Missing required field: {field}")
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Extract parameters
        start_date = data['start_date']
        end_date = data['end_date']
        event_types = data['event_type']
        user_addresses = []
        for addr in data['user_addresses']:
            if Web3.is_address(addr):
                user_addresses.append(Web3.to_checksum_address(addr))
            else:
                logger.error(f"Invalid address provided: {addr}")
                raise ValueError(f"Invalid address: {addr}")
        display_tx_column = data['display_tx_column']
        
        # Validate date formats
        try:
            datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except ValueError as e:
            logger.error(f"Invalid date format provided - start_date: {start_date}, end_date: {end_date}")
            return jsonify({'error': 'Invalid date format. Use ISO datetime format.'}), 400
        
        # Validate event_type and user_addresses are lists
        if not isinstance(event_types, list):
            logger.error(f"event_type is not a list: {type(event_types)}")
            return jsonify({'error': 'event_type must be a list'}), 400
        
        if not isinstance(user_addresses, list):
            logger.error(f"user_addresses is not a list: {type(user_addresses)}")
            return jsonify({'error': 'user_addresses must be a list'}), 400
        
        if not isinstance(display_tx_column, bool):
            logger.error(f"display_tx_column is not a boolean: {type(display_tx_column)}")
            return jsonify({'error': 'display_tx_column must be a boolean'}), 400
        
        # Get blockchain contracts and realtokens from app config
        blockchain_contracts = current_app.config['BLOCKCHAIN_CONTRACTS']
        realtokens = current_app.config['REALTOKENS']

        events_seller = get_accepted_offers_by_seller_datetime(current_app.config['DB_PATH'], user_addresses, start_date, end_date)
        events_buyer = get_accepted_offers_by_buyer_datetime(current_app.config['DB_PATH'], user_addresses, start_date, end_date)
        
        # Format dates for display
        from_datetime_formatted_string = datetime.fromisoformat(start_date.replace('Z', '+00:00')).strftime("%d %B %Y").lstrip('0')
        to_datetime_formatted_string = datetime.fromisoformat(end_date.replace('Z', '+00:00')).strftime("%d %B %Y").lstrip('0')

        # Create elements of the PDF
        elements = create_report_elements(
            user_addresses,
            from_datetime_formatted_string,
            to_datetime_formatted_string,
            events_buyer,
            events_seller,
            blockchain_contracts,
            realtokens,
            transaction_type_to_display=event_types,
            display_tx_hash=display_tx_column
        )
        
        # Build the PDF
        pdf_file = build_pdf(elements)
        
        # Create a BytesIO object to serve the PDF
        pdf_buffer = io.BytesIO(pdf_file)
        pdf_buffer.seek(0)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d")
        filename = f"YAM_transactions_report_{timestamp}.pdf"
        
        logger.info(f"Report generated successfully for addresses: {user_addresses}")
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        current_app.logger.error(f"Error generating report: {str(e)}")
        return jsonify({'error': f'Internal server error occurred while generating report: {e}'}), 400

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    logger.info("Health check requested")
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@api_bp.errorhandler(400)
def bad_request(error):
    logger.error(f"Bad request error: {error}")
    return jsonify({'error': 'Bad request'}), 400

@api_bp.errorhandler(404)
def not_found(error):
    logger.error(f"Endpoint not found: {error}")
    return jsonify({'error': 'Endpoint not found'}), 404

@api_bp.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500